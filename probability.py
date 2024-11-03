import math
import random
from typing import Callable, Iterable
from manim import *

from lib.animations import WaveInDirection
from lib.utils import colored_tex, style_exposition

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
        p = 0.5
        n = 10
        pdf = binomialDistribution(p, n)
        domain = list( range(n + 1)  )

        chart = InverseTransformChart( 
            domain, pdf,
            y_range=[0, 1, 0.2],
            y_length=5, x_length=4,
            bar_colors=barColors,
            bar_width=0.9,
        )
        chart.to_edge(RIGHT, 1)

        self.play(Create(chart))
        self.wait()

        # text = style_exposition( VGroup(
        #     colored_tex( r"We want to pick a value on the x-axis", 
        #         t2c={"x-axis":YELLOW} ),
        #     colored_tex( r"according to a given probability distribution.", 
        #         t2c={"probability distribution":YELLOW} ),
        # ).arrange(DOWN) ).to_edge(LEFT, 1)
        # self.play( Write( text[0] ) )
        # self.wait()

        # self.play( chart.animateXAxisWave() )
        # self.wait()

        # self.play( Write( text[1] ) )
        # self.wait()

        # self.play( chart.animateBarWave() )
        # self.wait()

        # self.play( FadeOut(text) )
        # text = style_exposition( VGroup(
        #     colored_tex( r"One way to do this is to stack up each bar," ),
        #     colored_tex( r"and uniformly pick a random y from 0 to 1.", 
        #         t2c={"y":YELLOW} ),
        # ).arrange(DOWN) ).to_edge(LEFT, 1)

        # self.play( Write( text[0] ) )
        # self.wait()

        # self.play( chart.animateStack(vertical=True) )
        # self.wait()

        # self.play( Write( text[1] ) )
        # self.wait()

        # self.play( chart.animateYAxisWave() )
        # self.wait()

        # self.play( chart.animateSelect(0.7, slow=True) )
        # self.wait()
        
        # self.play( FadeOut(text) )
        # text = style_exposition( VGroup(
        #     colored_tex( r"We select whichever bar this hits." ),
        #     colored_tex(
        #         r"This way,", r" the probability of a bar being\\", 
        #         r"selected is proportional to its height."
        #     ),
        # ).arrange(DOWN, 1) ).to_edge(LEFT, 1)

        # self.play( Write( text[0] ) )
        # self.wait()

        # self.play( Wiggle(chart.hitBar) )

        # self.play( Write( text[1][0] ) )
        # self.play( Write( text[1][1:], run_time=3 ) )
        # self.wait()

        # chart.addBraces()
        # self.play( chart.animateInBraces() )
        # self.wait()

        # self.play( FadeOut(chart.braces) )

        # self.play( FadeOut(text) )
        # hitStr = str(chart.hitIndex)
        # text = style_exposition( VGroup(
        #     colored_tex( r"Putting everything back,", "" ),
        #     colored_tex( r"we can see we've selected " + hitStr + ".",
        #         t2c={hitStr:YELLOW} )
        # ).arrange(DOWN) ).to_edge(LEFT, 2)
        
        # self.play( Write( text[0] ) )

        # self.play( chart.animateUnstack(), FadeOut(chart.selector) )
        # self.wait()

        # self.play( Write( text[1] ) )

        # self.play( Flash(chart.hitLabel) )
        # self.wait()

        # self.play( chart.animateUnhighlight() )
        # self.wait()

        # self.play( FadeOut(text) )
        text = style_exposition( colored_tex(
            r"To better connect this to the CDF,\\",
            r"it will help to instead stack the\\",
            r"bars like this..."
        ) ).to_edge(LEFT, 1)

        self.play( Write(text[0]) )
        self.play( Write(text[1:], run_time=3) )
        
        self.play( chart.animateStack(vertical=False) )
        self.wait()

        self.play( FadeOut(text) )
        text = style_exposition( colored_tex(
            r"What we're doing is finding where the\\",
            r"sampled y value intersects the CDF\\",
            r"of our distribution."
        ) ).to_edge(LEFT, 1)
        self.play( Write( text, run_time=4 ) )

        self.play( Create( chart.addCDFPlot( color=BLUE ) ) )

        self.play( chart.animateSelect( 0.5, False, includeVertical=True ) )

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
            **kwargs
        )

        self.y_axis.remove(self.y_axis.numbers)
        numbers = self.y_axis.numbers
        self.y_axis.add_numbers([0], excluding=[])
        for number in numbers:
            self.y_axis.numbers.add(number)

        self.y_axis.add_ticks()

        self.refBars = self.bars.copy().set_opacity(0)
        self.add(self.refBars)
    
    def addCDFPlot(self, **kwargs):
        self.cdfPlot = self.plot( 
            self.cdf,
            x_range=[0, self.count, 0.01], 
            use_smoothing=False,
            **kwargs
        )
        self.add(self.cdfPlot)
        return self.cdfPlot
    
    def addBraces(self):
        self.braces = VGroup()
        for bar in self.bars:
            if bar.height >= 0.1:
                brace = Brace(bar.copy().scale(0.95), RIGHT, sharpness=0.2)
                self.braces.add( brace )
        self.add(self.braces)
        return self.braces
    
    def animateInBraces(self):
        return LaggedStart( *[ FadeIn(brace, shift=LEFT) for brace in self.braces ] )
    
    def animateStack(self, vertical=False):
        height = 0
        anims = []
        centerBar = self.bars[ self.count // 2 ]
        for bar in self.bars:
            anim = bar.animate.shift(height * UP)
            if vertical:
                anim.move_to( centerBar, coor_mask=RIGHT )
            anims.append( anim )
            height += bar.height
        return LaggedStart( *anims )

    def animateUnstack(self):
        return LaggedStart( *[
            self.bars[i].animate.move_to( self.refBars[i] )
            for i in range( self.count )
        ] )
    
    def animateSelect(self, selection, slow=False, includeVertical=False):
        self.selection = selection

        self.hitIndex = select(self.values, selection)
        self.hitBar = self.bars[self.hitIndex]
        self.hitBar.set_z_index(1)
        self.hitLabel = self.x_axis.labels[self.hitIndex]
        
        lineStart = self.c2p(0, selection)
        if includeVertical:
            hitx = self.hitBar.get_center()[0]
            hity = lineStart[1]
            lineEnd = np.array([hitx, hity, 0])
        else:
            lineEnd = self.c2p(self.count, selection)
        self.selectorDot = Dot(color=YELLOW).move_to(lineStart)
        self.selectorLine =  DashedLine(lineStart, lineEnd, color=YELLOW)
        self.selector = VGroup(self.selectorDot, self.selectorLine)
        self.add(self.selector)

        dotAnim = FadeIn( self.selectorDot, shift=RIGHT*2 )
        lineAnim = FadeIn( self.selectorLine )
        barAnim = self.hitBar.animate.set_color(YELLOW)
        
        if slow:
            return Succession( dotAnim, lineAnim, barAnim, run_time=3 )
        else:
            return AnimationGroup( dotAnim, lineAnim, barAnim )
    
    def animateUnhighlight(self):
        return self.hitBar.animate.set_color( self.refBars[self.hitIndex].get_color() )
    
    def animateYAxisWave(self):
        self.y_axis.remove(self.y_axis.numbers)
        return WaveInDirection( 
            self.y_axis.numbers, UP, LEFT,
            _on_finish=lambda scene: self.y_axis.add(self.y_axis.numbers)
        )
    
    def animateXAxisWave(self):
        labels = self.x_axis.labels
        self.x_axis.remove(labels)
        return ApplyWave( 
            labels,
            _on_finish=lambda scene: self.x_axis.add(labels)
        )
    
    def animateBarWave(self):
        bars = self.bars
        bars.set_z_index(-1)
        self.remove(bars)
        return ApplyWave( 
            bars, 
            _on_finish=lambda scene: self.add(bars)
        )