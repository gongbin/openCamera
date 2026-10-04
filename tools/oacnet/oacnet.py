# SPDX-License-Identifier: Apache-2.0
"""oacnet: 一个只依赖标准库的「原理图即代码」小工具。

用 Python 描述器件和网络，做基本的电气规则检查，并导出：
  - KiCad 网表（.net，可在 Pcbnew 里「导入网表」）
  - BOM（CSV）
  - 引脚核对清单（CSV）
  - 按网络列出的可读网表（Markdown）

Python >= 3.8，无第三方依赖。
"""
import csv
import os
from collections import OrderedDict, defaultdict

# 引脚类型
PWR_IN, PWR_OUT, IN, OUT, BIDIR, PASSIVE, OD, NOCONN = (
    "power_in", "power_out", "input", "output", "bidirectional",
    "passive", "open_collector", "no_connect")

NC = object()  # 显式声明「此引脚悬空」


class PartDef(object):
    def __init__(self, name, prefix, pins, footprint="", mpn="", mfr="",
                 desc="", verified=False, note=""):
        self.name, self.prefix, self.footprint = name, prefix, footprint
        self.mpn, self.mfr, self.desc = mpn, mfr, desc
        self.verified, self.note = verified, note
        self.pins = [(str(n), nm, t) for n, nm, t in pins]


class Part(object):
    def __init__(self, ckt, pdef, ref, value, dnp=False):
        self.ckt, self.pdef, self.ref, self.dnp = ckt, pdef, ref, dnp
        self.value = value or pdef.name
        self.conn = {}  # 引脚编号 -> 网络名 或 NC

    def _nums(self, key):
        key = str(key)
        nums = [n for n, nm, _ in self.pdef.pins if nm == key]
        if not nums:
            nums = [n for n, _, _ in self.pdef.pins if n == key]
        if not nums:
            raise KeyError("%s (%s) 没有引脚 %s" % (self.ref, self.pdef.name, key))
        return nums

    def connect(self, mapping):
        """mapping: {引脚名或编号: 网络名 | NC}。同名引脚会一起连接。"""
        for key, net in mapping.items():
            for n in self._nums(key):
                if n in self.conn:
                    raise ValueError("%s 引脚 %s 重复连接" % (self.ref, n))
                self.conn[n] = net
        return self


class Circuit(object):
    def __init__(self, name):
        self.name = name
        self.parts = []
        self._count = defaultdict(int)
        self.sources = set()   # 声明为「有电源驱动」的网络
        self.single_ok = set() # 允许只有一个节点的网络

    def power(self, *nets):
        self.sources.update(nets)

    def allow_single(self, *nets):
        self.single_ok.update(nets)

    def add(self, pdef, mapping, value=None, dnp=False):
        self._count[pdef.prefix] += 1
        ref = "%s%d" % (pdef.prefix, self._count[pdef.prefix])
        p = Part(self, pdef, ref, value, dnp)
        self.parts.append(p)
        return p.connect(mapping)

    # ---- 分析 ----
    def nets(self):
        nets = OrderedDict()
        for p in self.parts:
            for num, name, typ in p.pdef.pins:
                net = p.conn.get(num)
                if net is None or net is NC:
                    continue
                nets.setdefault(net, []).append((p, num, name, typ))
        return nets

    def check(self):
        errors, warnings = [], []
        for p in self.parts:
            for num, name, typ in p.pdef.pins:
                if num not in p.conn:
                    errors.append("%s.%s(%s) 未连接也未声明 NC" % (p.ref, name, num))
                elif typ == NOCONN and p.conn[num] is not NC:
                    errors.append("%s.%s(%s) 是 NC 引脚却接了网络" % (p.ref, name, num))
        for net, nodes in self.nets().items():
            types = [t for _, _, _, t in nodes]
            if len(nodes) == 1 and net not in self.single_ok:
                p, num, name, _ = nodes[0]
                warnings.append("网络 %s 只有一个节点 (%s.%s)" % (net, p.ref, name))
            if types.count(OUT) + types.count(PWR_OUT) > 1:
                errors.append("网络 %s 有多个输出驱动" % net)
            if PWR_IN in types and PWR_OUT not in types and net not in self.sources:
                errors.append("网络 %s 上有电源输入引脚，但没有电源驱动" % net)
            if IN in types and not set(types) & {OUT, PWR_OUT, BIDIR, OD, PASSIVE} \
                    and net not in self.sources:
                warnings.append("网络 %s 上的输入引脚没有驱动" % net)
        return errors, warnings

    # ---- 导出 ----
    def export_kicad(self, path):
        def q(s):
            return '"%s"' % str(s).replace('"', "'")
        out = ['(export (version "E")',
               '  (design (source %s) (tool "oacnet"))' % q(self.name),
               '  (components']
        for p in self.parts:
            out.append('    (comp (ref %s) (value %s) (footprint %s)'
                       % (q(p.ref), q(p.value), q(p.pdef.footprint)))
            out.append('      (fields (field (name "MPN") %s) (field (name "DNP") %s)))'
                       % (q(p.pdef.mpn), q("1" if p.dnp else "0")))
        out.append('  )\n  (nets')
        for i, (net, nodes) in enumerate(self.nets().items(), 1):
            out.append('    (net (code %s) (name %s)' % (q(i), q(net)))
            for p, num, name, typ in nodes:
                out.append('      (node (ref %s) (pin %s) (pinfunction %s) (pintype %s))'
                           % (q(p.ref), q(num), q(name), q(typ)))
            out.append('    )')
        out.append('  )\n)')
        _write(path, "\n".join(out) + "\n")

    def export_bom(self, path):
        groups = OrderedDict()
        for p in self.parts:
            key = (p.pdef.name, p.value, p.pdef.footprint, p.pdef.mpn, p.dnp)
            groups.setdefault(key, []).append(p)
        rows = [["位号", "数量", "名称", "值", "封装", "厂商", "料号", "不贴", "说明"]]
        for (name, value, fp, mpn, dnp), ps in groups.items():
            d = ps[0].pdef
            rows.append([" ".join(x.ref for x in ps), len(ps), name, value, fp,
                         d.mfr, mpn, "是" if dnp else "", d.desc])
        _write_csv(path, rows)

    def export_pin_review(self, path):
        rows = [["器件", "料号", "位号", "引脚编号已对照数据手册", "封装", "备注"]]
        seen = OrderedDict()
        for p in self.parts:
            seen.setdefault(p.pdef, []).append(p.ref)
        for d, refs in seen.items():
            if d.prefix in ("R", "C", "TP"):
                continue
            rows.append([d.name, d.mpn, " ".join(refs),
                         "是" if d.verified else "否", d.footprint, d.note])
        _write_csv(path, rows)

    def export_markdown(self, path):
        out = ["# %s 网表（自动生成，勿手改）" % self.name, "",
               "| 网络 | 节点 |", "|---|---|"]
        for net, nodes in sorted(self.nets().items()):
            out.append("| `%s` | %s |" % (net, ", ".join(
                "%s.%s" % (p.ref, name if name == num else "%s(%s)" % (name, num))
                for p, num, name, _ in nodes)))
        _write(path, "\n".join(out) + "\n")


def _write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _write_csv(path, rows):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)
