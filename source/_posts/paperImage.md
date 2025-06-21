---
title: 论文图片
date: 2021-05-18 21:27:57
tags: [绘图,python]
---
> 最近和W博交流，看了一下他发的顶会论文，发现了一些绘图的小tricks。有感而发。

一般会发现比较好的期刊上的图中，文字都是能选中的，而且非常清晰。这些不是纯粹图片格式，这种一般都是矢量图。我之前虽然知道这是矢量图，但是并不知道python绘图可以保存矢量图，python中的matplotlib库其实是支持导出矢量图的，保存为pdf格式或者eps就可以。

```python
plt.savefig(filename,format='eps/pdf')
```

在使用visio等软件画流程图、示意图的时候，也是支持矢量图导出的。

值得注意的是，因为保存的是矢量图，所以会有字体的信息，matplotlib默认会保存Type3字体,这时候你在投稿pdf到某些审稿系统时，会出现字体缺失的情况，这样你的图里就没字或者直接整个pdf就崩溃了。可以考虑[这里](http://phyletica.org/matplotlib-fonts/)的解决方案。简而言之就是把字体换成Type47。

```python
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
```
