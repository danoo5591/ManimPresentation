#!/usr/bin/env python

from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim presentacion_tesis.py <class_name> -pl
#
# Use the flat -l for a faster rendering at a lower
# quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the n'th animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1080
# for a 1920x1080 video)

"""
<a href="https://miktex.org/download">Getting MiKTeX - MiKTeX.org</a><br/>
<a href="https://www.youtube.com/watch?v=ENMyFGmq5OA&list=PL2B6OzTsMUrwo4hA3BBfS7ZR34K361Z8F">Manim tutorial | Introduction: What is Manim? - YouTube</a><br/>
<a href="https://gilberttanner.com/blog/creating-math-animations-in-python-with-manim">Creating math animations in Python with Manim</a><br/>
<a href="https://github.com/malhotra5/Manim-Tutorial#Running-Manim-Projects">GitHub - malhotra5/Manim-Tutorial: A tutorial for manim, a mathematical animation engine made by 3b1b</a><br/>
<a href="https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/">Getting Started Animating with manim and Python 3.7 | Talking Physics</a><br/>
<a href="https://manim.readthedocs.io/en/latest/getting_started/">Getting Started &mdash; Manim documentation</a><br/>
<a href="https://towardsdatascience.com/amazing-math-visuals-4aba53c48c43">Amazing Math Visuals. Manim helps you to create stylish maths&hellip; | by Sergio Capape | Towards Data Science</a><br/>
<a href="https://www.youtube.com/watch?v=lF49gHBZBpI&list=PLcjmqHFN9VeMC9znnNiRMv3nqZv-bU9Fo&index=4">Tutorial de Manim | 1.1 - Elementos b&aacute;sicos - YouTube</a><br/>
<a href="https://www.youtube.com/watch?v=bBC-nXj3Ng4">But how does bitcoin actually work? - YouTube</a><br/>
<a href="https://github.com/malhotra5/Manim-Tutorial">GitHub - malhotra5/Manim-Tutorial: A tutorial for manim, a mathematical animation engine made by 3b1b</a><br/>
<a href="https://www.google.com/search?q=manim+big+main+title&ei=UJxmX4rrFaTD5OUPk_C-4A8&start=10&sa=N&ved=2ahUKEwiK06S1t_brAhWkIbkGHRO4D_wQ8NMDegQIDBBD&biw=1600&bih=797">manim big main title - Buscar con Google</a><br/>
<a href="https://gist.github.com/Adirockzz95/06649145d7e6c4c147c02459fd2bc5af">manim animation examples &middot; GitHub</a><br/>
<a href="https://talkingphysics.wordpress.com/2018/06/14/creating-text-manim-series-part-4/">Creating Text &ndash; manim Series: Part 4 | Talking Physics</a><br/>
<a href="https://news.ycombinator.com/item?id=19716019">Manim &ndash; 3Blue1Brown&#39;s animation engine for explanatory math videos | Hacker News</a><br/>
<a href="https://laptrinhx.com/a-tutorial-for-manim-a-mathematical-animation-engine-made-by-3b1b-1406894766/">laptrinhx.com</a><br/>
<a href="https://laptrinhx.com/a-tutorial-for-manim-a-mathematical-animation-engine-made-by-3b1b-1406894766/">laptrinhx.com</a><br/>
<a href="https://news.ycombinator.com/item?id=19716019">Manim &ndash; 3Blue1Brown&#39;s animation engine for explanatory math videos | Hacker News</a><br/>
<a href="https://www.google.com/search?biw=1600&bih=797&ei=ecBmX8v_NOHL5OUP24qV4A0&q=manim+example+github&oq=manim+example+github&gs_lcp=CgZwc3ktYWIQAzoCCAA6CAgAEBYQChAeOgYIABAWEB46BAgAEAo6BQghEKABOgQIIRAVOgcIIRAKEKABUK8wWMlFYMhGaABwAXgAgAHiAYgBqQySAQYxMi4zLjGYAQCgAQGqAQdnd3Mtd2l6wAEB&sclient=psy-ab&ved=0ahUKEwiLoM7z2fbrAhXhJbkGHVtFBdw4ChDh1QMIDQ&uact=5">manim example github - Buscar con Google</a><br/>
<a href="https://talkingphysics.wordpress.com/2018/06/14/creating-text-manim-series-part-4/">Creating Text &ndash; manim Series: Part 4 | Talking Physics</a><br/>
<a href="https://github.com/zimmermant/manim_tutorial/blob/master/manim_tutorial_P37.py">manim_tutorial/manim_tutorial_P37.py at master &middot; zimmermant/manim_tutorial &middot; GitHub</a><br/>
<a href="https://github.com/malhotra5/Manim-Tutorial#Text">GitHub - malhotra5/Manim-Tutorial: A tutorial for manim, a mathematical animation engine made by 3b1b</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimationsWithManim">GitHub - Elteoremadebeethoven/AnimationsWithManim: Animation course with Manim</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimationsWithManim/blob/master/English/3_text_like_arrays/scenes.md">AnimationsWithManim/scenes.md at master &middot; Elteoremadebeethoven/AnimationsWithManim &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimationsWithManim/blob/master/English/4_transform/scenes.md">AnimationsWithManim/scenes.md at master &middot; Elteoremadebeethoven/AnimationsWithManim &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimationsWithManim/blob/master/English/5_visual_tools/scenes.md">AnimationsWithManim/scenes.md at master &middot; Elteoremadebeethoven/AnimationsWithManim &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/Manim-TB">GitHub - Elteoremadebeethoven/Manim-TB: My version of Manim (by 3b1b)</a><br/>
<a href="https://towardsdatascience.com/amazing-math-visuals-4aba53c48c43">Amazing Math Visuals. Manim helps you to create stylish maths&hellip; | by Sergio Capape | Towards Data Science</a><br/>
<a href="https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/">Getting Started Animating with manim and Python 3.7 | Talking Physics</a><br/>
<a href="https://gilberttanner.com/blog/creating-math-animations-in-python-with-manim">Creating math animations in Python with Manim</a><br/>
<a href="https://www.youtube.com/watch?v=fNk_zzaMoSs&list=PLfeOMjqemCOOb7G93waDrLLu5ZdOzuPp0&index=15">Vectors, what even are they? | Essence of linear algebra, chapter 1 - YouTube</a><br/>
<a href="https://github.com/Elteoremadebeethoven">Elteoremadebeethoven (Alexander V&aacute;zquez) &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimationsWithManim/blob/master/English/4_transform/scenes.md">AnimationsWithManim/scenes.md at master &middot; Elteoremadebeethoven/AnimationsWithManim &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/MyAnimations">GitHub - Elteoremadebeethoven/MyAnimations: In this repository you will find the code and files of my own animations of manim</a><br/>
<a href="https://github.com/Elteoremadebeethoven/MyAnimations/blob/master/my_projects/my_animations.py">MyAnimations/my_animations.py at master &middot; Elteoremadebeethoven/MyAnimations &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/MyAnimations/tree/master/quadratic_equation">MyAnimations/quadratic_equation at master &middot; Elteoremadebeethoven/MyAnimations &middot; GitHub</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimacionesConManim">GitHub - Elteoremadebeethoven/AnimacionesConManim: Curso de animaci&oacute;n en Manim</a><br/>
<a href="https://github.com/Elteoremadebeethoven/Manim-TB">GitHub - Elteoremadebeethoven/Manim-TB: My version of Manim (by 3b1b)</a><br/>
<a href="https://github.com/Elteoremadebeethoven/AnimacionesConManim">GitHub - Elteoremadebeethoven/AnimacionesConManim: Curso de animaci&oacute;n en Manim</a><br/>
<a href="https://drive.google.com/file/d/1O31Hk95q6D3Z6qWwkZcUW4fU9lLzJND2/view">tutorial_esp.zip - Google Drive</a><br/>
<a href="chrome://newtab/">Nueva pesta&ntilde;a</a><br/>
<a href="https://www.youtube.com/watch?v=lF49gHBZBpI&list=PLcjmqHFN9VeMC9znnNiRMv3nqZv-bU9Fo&index=4">Tutorial de Manim | 1.1 - Elementos b&aacute;sicos - YouTube</a><br/>
<a href="https://github.com/Elteoremadebeethoven/Manim-TB">GitHub - Elteoremadebeethoven/Manim-TB: My version of Manim (by 3b1b)</a><br/>
<a href="https://www.google.com/search?ei=WsxmX9TnC6fH5OUP-6CpYA&q=display+item+list+Manim&oq=display+item+list+Manim&gs_lcp=CgZwc3ktYWIQAzoGCAAQBxAeOggIABAIEAcQHjoKCAAQBxAFEAoQHjoGCAAQCBAeOggIABAIEAoQHlDKkAFY4cwBYOjNAWgLcAB4AIABcYgBzxOSAQQyMC44mAEAoAEBqgEHZ3dzLXdpesABAQ&sclient=psy-ab&ved=0ahUKEwjU_Kyd5fbrAhWnI7kGHXtQCgwQ4dUDCA0&uact=5">display item list Manim - Buscar con Google</a><br/>
<a href="https://github.com/3b1b/manim/blob/master/manimlib/for_3b1b_videos/common_scenes.py">manim/common_scenes.py at master &middot; 3b1b/manim &middot; GitHub</a><br/>
<a href="https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/">Getting Started Animating with manim and Python 3.7 | Talking Physics</a><br/>
<a href="https://stackoverflow.com/questions/tagged/manim?tab=newest&page=2&pagesize=15">Newest &#39;manim&#39; Questions - Page 2 - Stack Overflow</a><br/>
<a href="https://stackoverflow.com/questions/63462538/novice-question-regarding-manim-and-png-images">python - Novice question regarding manim and png images - Stack Overflow</a><br/>
<a href="https://github.com/3b1b/manim/pull/1112">Add dot_color to BulletedList by vivek3141 &middot; Pull Request #1112 &middot; 3b1b/manim &middot; GitHub</a><br/>
<a href="https://www.reddit.com/r/manim/comments/bselso/manim_tutorial_13_positions_rotations_and_fonts/">Manim tutorial | 1.3 Positions, rotations and fonts : manim</a><br/>
<a href="https://github.com/3b1b/manim/blob/master/example_scenes.py">manim/example_scenes.py at master &middot; 3b1b/manim &middot; GitHub</a><br/>
<a href="https://www.google.com/search?q=manim+LaggedStart&oq=manim+LaggedStart&aqs=chrome..69i57.1028j0j1&sourceid=chrome&ie=UTF-8">manim LaggedStart - Buscar con Google</a><br/>
<a href="https://www.google.com/search?ei=7tJmX-6bKv3F5OUP4_q82A4&q=manim+LaggedStart%28ApplyMethod&oq=manim+LaggedStart%28ApplyMethod&gs_lcp=CgZwc3ktYWIQAzoHCCEQChCgAVCezQFYk7MCYNa0AmgAcAB4AIABfIgBmg-SAQQyMC40mAEAoAECoAEBqgEHZ3dzLXdpesABAQ&sclient=psy-ab&ved=0ahUKEwjuysrA6_brAhX9IrkGHWM9D-sQ4dUDCA0&uact=5">manim LaggedStart(ApplyMethod - Buscar con Google</a><br/>
<a href="https://www.google.com/search?q=type+object+%27ApplyMethod%27+has+no+attribute+%27mobject%27&oq=type+object+%27ApplyMethod%27+has+no+attribute+%27mobject%27&aqs=chrome..69i57.119j0j1&sourceid=chrome&ie=UTF-8">type object &#39;ApplyMethod&#39; has no attribute &#39;mobject&#39; - Buscar con Google</a><br/>
<a href="https://talkingphysics.wordpress.com/2018/06/14/creating-text-manim-series-part-4/">Creating Text &ndash; manim Series: Part 4 | Talking Physics</a><br/>
<a href="https://github.com/3b1b/manim/blob/master/manimlib/for_3b1b_videos/common_scenes.py">manim/common_scenes.py at master &middot; 3b1b/manim &middot; GitHub</a><br/>
<a href="https://www.google.com/search?q=Manim+transform+text+color&oq=Manim+transform+text+color&aqs=chrome..69i57.5757j0j1&sourceid=chrome&ie=UTF-8">Manim transform text color - Buscar con Google</a><br/>
<a href="https://github.com/malhotra5/Manim-Tutorial">GitHub - malhotra5/Manim-Tutorial: A tutorial for manim, a mathematical animation engine made by 3b1b</a><br/>
<a href="https://github.com/malhotra5/Manim-Guide">GitHub - malhotra5/Manim-Guide: A documentation of the most common Manim functionalities such as classes and methods.</a><br/>
<a href="https://www.google.com/search?q=manim+position&oq=manim+position&aqs=chrome..69i57.1913j0j1&sourceid=chrome&ie=UTF-8">manim position - Buscar con Google</a><br/>
<a href="https://www.youtube.com/watch?v=gIvQsqXy5os">Manim tutorial | 1.3 Positions, rotations and fonts - YouTube</a><br/>
<a href="https://talkingphysics.wordpress.com/2018/06/14/creating-text-manim-series-part-4/">Creating Text &ndash; manim Series: Part 4 | Talking Physics</a><br/>
<a href="https://www.google.com/search?q=github&oq=github&aqs=chrome..69i57j69i59l2j69i65j69i60l2.3024j0j1&sourceid=chrome&ie=UTF-8">github - Buscar con Google</a><br/>

"""

class MainPresentation(Scene):
    def construct(self):
            title = TextMobject(r"\textsc{Analísis de opiniones a nivel de aspectos}")
            title.scale(1.2)
            self.play(Write(title))
            self.wait(0.2)
            self.play(
                title.set_color, BLUE,
                run_time=0.6
            )
            self.wait(0.5)
            self.play(
                title.to_edge, UP,
                title.scale, 0.8,
                title.set_color, WHITE,
                run_time=0.6
            )
        

class OpeningManimExample(Scene):
    def construct(self):
        title = TextMobject("This is some \\LaTeX")
        basel = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeInFrom(basel, UP),
        )
        self.wait()

        transform_title = TextMobject("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(*map(FadeOutAndShiftDown, basel)),
        )
        self.wait()

        grid = NumberPlane()
        grid_title = TextMobject("This is a grid")
        grid_title.scale(1.5)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title),
            FadeInFromDown(grid_title),
            ShowCreation(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = TextMobject(
            "That was a non-linear function \\\\"
            "applied to the grid"
        )
        grid_transform_title.move_to(grid_title, UL)
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.apply_function,
            lambda p: p + np.array([
                np.sin(p[1]),
                np.sin(p[0]),
                0,
            ]),
            run_time=3,
        )
        self.wait()
        self.play(
            Transform(grid_title, grid_transform_title)
        )
        self.wait()


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = TextMobject(
            "This is a some text",
            tex_to_color_map={"text": YELLOW}
        )
        example_tex = TexMobject(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UpdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()

# See old_projects folder for many, many more
