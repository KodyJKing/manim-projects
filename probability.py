import math
import random
from typing import Callable, Iterable
from manim import *

stdnormal = lambda x: math.exp( -x*x / 2 ) / math.sqrt(TAU)

def binomialDistribution(p, n):
    q = 1 - p
    return lambda k: math.comb(n, k) * math.pow(p, k) * math.pow(q, n - k)

def uniformDistribution(n):
    return lambda k: 1 / (n + 1)

def rampDistribution(n):
    tri = (n + 1) * n / 2
    return lambda k: k / tri

barColors = [
    "#4B90A7",
    "#4B90A7",
    "#24963D",
    "#A98E4B",
    "#A98E4B",
]

def select(values, u):
    s = 0
    for i in range( len(values) ):
        v = values[i]
        s += v
        if  s >= u:
            return i

def cumulative(values):
    result = []
    s = 0
    for v in values:
        s += v
        result.append(s)
    return result

def listToFunction(values):
    def fn(x):
        x = x - 0.5
        if x < 0:
            return 0
        if x >= len(values):
            return 1
        return values[math.floor(x)]
    return fn

class DiscreteSampling(Scene):
    def construct(self):
        random.seed(68)

        p = 0.5
        n = 10
        func = binomialDistribution(p, n)
        # func = rampDistribution(n)
        domain = list( range(n + 1)  )
        values = list( map( func, domain ) )
        cumulativeFunc = listToFunction(cumulative(values))
        chart = BarChart( 
            values = values,
            bar_names=domain,
            y_range=[0, 1, 0.2],
            y_length=5,
            x_length=5,
            bar_width=0.9,
            bar_colors=barColors
        )
        chart.to_edge(RIGHT, 2)
        xaxis, yaxis = chart.axes
        yaxis.add_numbers([0], excluding=[])

        self.play( FadeIn(chart) )
        self.wait()

        bars = chart.bars.copy()
        targetBar = bars[ n // 2 ]

        def showCumulativePlot():
            plot = chart.plot( 
                cumulativeFunc,
                x_range=[0, n+1, 0.01], 
                use_smoothing=False,
                color=BLUE
            )
            self.play(FadeIn(plot))

        def playSelect(
            u,  slowVersion=False,
            stack=False, showPlot=False,
            showBraces=False,
        ):
            s = 0
            anims = []
            for bar in bars:
                anim = bar.animate.shift(s * UP)
                if stack:
                    anim.move_to( targetBar, coor_mask=RIGHT )
                anims.append( anim )
                s += bar.height

            if showPlot:
                showCumulativePlot()
                self.wait()
            
            # chart.bars.set_opacity(0.125 / 2)
            chart.bars.set_opacity(0)
            self.play(  LaggedStart( *anims ) )
            if slowVersion:
                self.wait()
                self.play( Indicate( yaxis, scale_factor=1.05 ) )

            lineStart = chart.c2p(0, u)
            lineEnd = chart.c2p(n + 1, u)
            dot = Dot(color=YELLOW).move_to( lineStart )
            line = DashedLine( lineStart, lineEnd, color=YELLOW )
            selector = VGroup(dot, line)

            hitIndex = select(values, u)
            hitBar = bars[hitIndex]
            hitBar.set_z_index(1)
            labels = chart.x_axis.labels
            hitLabel = labels[hitIndex]

            hitOriginalColor = hitBar.get_color()

            if slowVersion:
                self.play( GrowFromCenter(dot) )
                self.play( FadeIn(line), hitBar.animate.set_color(YELLOW) )

                if showBraces:
                    braces = VGroup()
                    anims = []
                    for bar in bars:
                        if bar.height >= 0.1:
                            sharpness = 0.2 / bar.height
                            brace = Brace(bar.copy().scale(0.95), RIGHT, sharpness=0.2)
                            braces.add( brace )
                            anims.append( FadeIn(brace, shift=LEFT) )
                    self.play( LaggedStart(*anims ) )
                    self.wait()
                    self.play( FadeOut( braces ) )
                    
                self.play( Wiggle( hitBar ) )
                self.wait()
            else:
                self.play(
                    GrowFromCenter(dot),
                    FadeIn(line),
                    hitBar.animate.set_color(YELLOW)
                )
            

            anims = []
            for i in range( len( bars ) ):
                bar = bars[i]
                original = chart.bars[i]
                anims.append( bar.animate.move_to(original) )
            
            self.play( 
                LaggedStart( *anims ), 
                FadeOut(selector),
                # selector.animate.set_opacity(0.25).set_color(GRAY),
                hitLabel.animate.set_color(YELLOW)
            )

            self.play( Flash(hitLabel) )
            if slowVersion:
                self.wait()

            self.play( 
                hitBar.animate.set_color( hitOriginalColor ),
                hitLabel.animate.set_color(WHITE)
            )
            if slowVersion:
                self.wait()

        playSelect(0.8,   slowVersion=True,  stack=True,  showBraces=True)
        playSelect(0.436, slowVersion=True,  stack=False )
        playSelect(0.225, slowVersion=False, stack=False, showPlot=True)

        # for i in range(4):
        #     playSelect( random.random() )

class InverseTransformChart(BarChart):
    def __init__(
        self,
        domain: Iterable[float],
        pdf: Callable[[float], float],
        **kwargs
    ):
        self.count = len(domain)
        self.domain = domain
        self.values = list( map( pdf, domain ) )
        self.cdf = listToFunction(cumulative(self.values))
        super().__init__(
            values = self.values,
            bar_names=domain,
            bar_colors=barColors,
            **kwargs
        )
    
    def addCumulativePlot(self, **kwargs):
        self.commulativePlot = self.plot( 
            self.cdf,
            x_range=[0, self.count, 0.01], 
            use_smoothing=False,
            **kwargs
        )
        return self.commulativePlot