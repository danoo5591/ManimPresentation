#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
import os
import sys
import inspect
from PIL import Image
import cv2
import random
from scipy.spatial.distance import cdist
from scipy import ndimage

sys.path.append(os.path.dirname(__file__))
from manimlib.imports import *

from efvgt import get_confetti_animations
from nn.network import *

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

class NetworkMobject(VGroup):
    CONFIG = {
        "neuron_radius" : 0.15,
        "neuron_to_neuron_buff" : MED_SMALL_BUFF,
        "layer_to_layer_buff" : LARGE_BUFF,
        "neuron_stroke_color" : BLUE,
        "neuron_stroke_width" : 3,
        "neuron_fill_color" : GREEN,
        "edge_color" : LIGHT_GREY,
        "edge_stroke_width" : 2,
        "edge_propogation_color" : YELLOW,
        "edge_propogation_time" : 1,
        "max_shown_neurons" : 16,
        "brace_for_large_layers" : True,
        "average_shown_activation_of_large_layer" : True,
        "include_output_labels" : False,
    }
    def __init__(self, neural_network, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.neural_network = neural_network
        self.layer_sizes = neural_network.sizes
        self.add_neurons()
        self.add_edges()

    def add_neurons(self):
        layers = VGroup(*[
            self.get_layer(size)
            for size in self.layer_sizes
        ])
        layers.arrange(RIGHT, buff = self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers)
        if self.include_output_labels:
            self.add_output_labels()

    def get_layer(self, size):
        layer = VGroup()
        n_neurons = size
        if n_neurons > self.max_shown_neurons:
            n_neurons = self.max_shown_neurons
        neurons = VGroup(*[
            Circle(
                radius = self.neuron_radius,
                stroke_color = self.neuron_stroke_color,
                stroke_width = self.neuron_stroke_width,
                fill_color = self.neuron_fill_color,
                fill_opacity = 0,
            )
            for x in range(n_neurons)
        ])   
        neurons.arrange(
            DOWN, buff = self.neuron_to_neuron_buff
        )
        for neuron in neurons:
            neuron.edges_in = VGroup()
            neuron.edges_out = VGroup()
        layer.neurons = neurons
        layer.add(neurons)

        if size > n_neurons:
            dots = TexMobject("\\vdots")
            dots.move_to(neurons)
            VGroup(*neurons[:len(neurons) // 2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*neurons[len(neurons) // 2:]).next_to(
                dots, DOWN, MED_SMALL_BUFF
            )
            layer.dots = dots
            layer.add(dots)
            if self.brace_for_large_layers:
                brace = Brace(layer, LEFT)
                brace_label = brace.get_tex(str(size))
                layer.brace = brace
                layer.brace_label = brace_label
                layer.add(brace, brace_label)

        return layer

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = self.get_edge(n1, n2)
                edge_group.add(edge)
                n1.edges_out.add(edge)
                n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_edge(self, neuron1, neuron2):
        return Line(
            neuron1.get_center(),
            neuron2.get_center(),
            buff = self.neuron_radius,
            stroke_color = self.edge_color,
            stroke_width = self.edge_stroke_width,
        )

    def get_active_layer(self, layer_index, activation_vector):
        layer = self.layers[layer_index].deepcopy()
        self.activate_layer(layer, activation_vector)
        return layer

    def activate_layer(self, layer, activation_vector):
        n_neurons = len(layer.neurons)
        av = activation_vector
        def arr_to_num(arr):
            return (np.sum(arr > 0.1) / float(len(arr)))**(1./3)

        if len(av) > n_neurons:
            if self.average_shown_activation_of_large_layer:
                indices = np.arange(n_neurons)
                indices *= int(len(av)/n_neurons)
                indices = list(indices)
                indices.append(len(av))
                av = np.array([
                    arr_to_num(av[i1:i2])
                    for i1, i2 in zip(indices[:-1], indices[1:])
                ])
            else:
                av = np.append(
                    av[:n_neurons//2],
                    av[-n_neurons//2:],
                )
        for activation, neuron in zip(av, layer.neurons):
            neuron.set_fill(
                color = self.neuron_fill_color,
                opacity = activation
            )
        return layer

    def activate_layers(self, input_vector):
        activations = self.neural_network.get_activation_of_all_layers(input_vector)
        for activation, layer in zip(activations, self.layers):
            self.activate_layer(layer, activation)

    def deactivate_layers(self):
        all_neurons = VGroup(*it.chain(*[
            layer.neurons
            for layer in self.layers
        ]))
        all_neurons.set_fill(opacity = 0)
        return self

    def get_edge_propogation_animations(self, index):
        edge_group_copy = self.edge_groups[index].copy()
        edge_group_copy.set_stroke(
            self.edge_propogation_color,
            width = 1.5*self.edge_stroke_width
        )
        return [ShowCreationThenDestruction(
            edge_group_copy, 
            run_time = self.edge_propogation_time,
            lag_ratio = 0.5
        )]

    def add_output_labels(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[-1].neurons):
            label = TexMobject(str(n))
            label.set_height(0.75*neuron.get_height())
            label.move_to(neuron)
            label.shift(neuron.get_width()*RIGHT)
            self.output_labels.add(label)
        self.add(self.output_labels)

class NetworkScene(Scene):
    CONFIG = {
        "layer_sizes" : [8, 7, 4, 3],
        "network_mob_config" : {},
    }
    def setup(self):
        self.add_network()

    def add_network(self):
        self.network = Network(sizes = self.layer_sizes)
        self.network_mob = NetworkMobject(
            self.network,
            **self.network_mob_config
        )
        self.add(self.network_mob)

    def feed_forward(self, input_vector, false_confidence = False, added_anims = None):
        if added_anims is None:
            added_anims = []
        activations = self.network.get_activation_of_all_layers(
            input_vector
        )
        if false_confidence:
            i = np.argmax(activations[-1])
            activations[-1] *= 0
            activations[-1][i] = 1.0
        for i, activation in enumerate(activations):
            self.show_activation_of_layer(i, activation, added_anims)
            added_anims = []

    def show_activation_of_layer(self, layer_index, activation_vector, added_anims = None):
        if added_anims is None:
            added_anims = []
        layer = self.network_mob.layers[layer_index]
        active_layer = self.network_mob.get_active_layer(
            layer_index, activation_vector
        )
        anims = [Transform(layer, active_layer)]
        if layer_index > 0:
            anims += self.network_mob.get_edge_propogation_animations(
                layer_index-1
            )
        anims += added_anims
        self.play(*anims)

    def remove_random_edges(self, prop = 0.9):
        for edge_group in self.network_mob.edge_groups:
            for edge in list(edge_group):
                if np.random.random() < prop:
                    edge_group.remove(edge)

def make_transparent(image_mob):
    alpha_vect = np.array(
        image_mob.pixel_array[:,:,0],
        dtype = 'uint8'
    )
    image_mob.set_color(WHITE)
    image_mob.pixel_array[:,:,3] = alpha_vect
    return image_mob


class underline(Line):
    # buff 0.07
    def __init__(self,texto,buff=0.09,**kwargs):
        Line.__init__(self,texto.get_corner(DL),texto.get_corner(DR),**kwargs)
        self.shift(DOWN*buff)


class MainPresentation(NetworkScene, MovingCameraScene):    
    CONFIG = {
        # "layer_sizes" : DEFAULT_LAYER_SIZES,
        "network_mob_config" : {
            "neuron_to_neuron_buff" : MED_LARGE_BUFF,
            "layer_to_layer_buff" : 1,
            "edge_stroke_width" : 1.2,
            "edge_propogation_color" : YELLOW_E,
            "edge_propogation_time" : 2,
        },
        "public_color" : GREEN,
        "private_color" : RED,
        "signature_color" : BLUE_C,
    }

    def setup(self):
        MovingCameraScene.setup(self)
        NetworkScene.setup(self)
        self.remove(self.network_mob)

    def construct(self):
        # self.show_quote()
        # self.remove_all_obj_in_scene()
        self.show_title()
        self.introduction()
        self.remove_all_obj_in_scene()
        self.show_amazon_example()
        self.remove_all_obj_in_scene()
        self.show_opinions_example()
        self.remove_all_obj_in_scene()
        self.show_def_opinion()
        self.show_words()
        self.show_network()
        self.show_input_document()
        self.show_output_layer()
        self.show_learning()
        self.remove_all_obj_in_scene()
        self.show_benefit()
        self.show_end()

    def remove_all_obj_in_scene(self):
        self.play(
            *[FadeOut(mob)for mob in self.mobjects]
            # All mobjects in the screen are saved in self.mobjects
        )
        self.wait()

    def show_quote(self):
        words = TextMobject(
            """
            ``We can only see a short distance ahead, \\\\ but we can see plenty there that needs to be done.''
            """, 
            organize_left_to_right = False
        )
        # words.to_edge(UP)    
        # words.set_width(2*(FRAME_X_RADIUS-1))      
        for mob in words.submobjects[27:27+11]:
            mob.set_color(GREEN)
        author = TextMobject("-Alan Turing")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words), run_time=1)
        self.wait()
        self.play(Write(author, run_time=1))
        self.wait()

    def show_title(self):
            universidad = TextMobject('\\small \\sc Universidad de la República')
            facultad = TextMobject('\\small \\sc Facultad de Ingeniería')

            title = TextMobject(
                "\\bf Estudio de las opiniones utilizando \\\\ Análisis de sentimientos a basado en aspectos"
            )

            autor = TextMobject('\\scriptsize por Danilo Amaral')
            
            grupo = TextMobject('\\footnotesize Grupo de Procesamiento de Lenguaje Natural')
            instituto = TextMobject('\\footnotesize Instituto de Computación')

            universidad.to_edge(UP)
            facultad.next_to(universidad,DOWN,buff=0.1)

            title.move_to(0.4*UP)
            autor.next_to(title, DOWN, buff=0.5)

            instituto.to_edge(DOWN)
            grupo.next_to(instituto, UP)

            self.play(
                FadeIn(universidad),
                FadeIn(facultad),
                FadeIn(title),
                FadeIn(autor),
                FadeIn(instituto),
                FadeIn(grupo), 
                run_time=0.5
            )
            # self.play(title.set_color, BLUE)
            self.wait()
            self.play(
                FadeOut(universidad),
                FadeOut(facultad),
                FadeOut(title),
                FadeOut(autor),
                FadeOut(instituto),
                FadeOut(grupo),
                run_time=0.5
            )
            self.wait()
    
    def introduction(self):
            question_1 = TextMobject('¿Que entendemos por ','"', 'Opinión', '"?')
            question_2 = TextMobject('¿Como definimos la "', 'Opinion', r'" de forma en que \\ una computadora lo entienda?')
            question_1[2].set_color(YELLOW)
            question_2[1].set_color(YELLOW)
            self.play(Write(question_1))
            self.wait()
            self.play(ReplacementTransform(question_1, question_2))
            self.wait(2)


    def show_amazon_example(self):
        background = ImageMobject("img/celular_amazon.png")
        background.set_height(FRAME_HEIGHT)
        self.play(FadeIn(background))
        self.wait(4)

        entity_rect = Rectangle(height=5.3, width=2.6)
        entity_rect.move_to(0.4*UP + 3.55*LEFT)
        entity = TextMobject("Entidad")
        entity.next_to(entity_rect, 0.3*DOWN)
        VGroup(entity, entity_rect).set_color(BLUE_E)

        self.play(ShowCreation(entity_rect), run_time=2)
        self.play(
            Write(entity),
        )
        self.wait(2)

        aspect_rect = Rectangle(height=2.56, width=4)
        aspect_rect.move_to(0.9*UP + 1.5*RIGHT)
        aspect = TextMobject("Aspectos")
        aspect.next_to(aspect_rect, 0.3*UP)
        aspect_group = VGroup(aspect, aspect_rect).set_color(GREEN_E)

        self.play(ShowCreation(aspect_rect), run_time=2)
        self.play(
            Write(aspect),
        )

        self.wait()

        # Save the state of camera
        self.camera_frame.save_state()

        # Animation of the camera
        self.play(
            # Set the size with the width of a object
            self.camera_frame.set_height,aspect_group.get_height()*1.2,
            # Move the camera to the object
            self.camera_frame.move_to,aspect_group
        )
        self.wait()
        
        # Add aspects lines
        aspect_lines = VGroup(*[Line(0.5*LEFT, 2.5*RIGHT) for i in range(5)])
        aspect_lines.set_color(GREEN_E)
        #.set_stroke(width=2)

        aspect_lines[0].move_to(0.05*DOWN + 1.1*RIGHT)
        aspect_lines[1].move_to(0.5*UP + 1.1*RIGHT)
        aspect_lines[2].move_to(1.05*UP + 1.1*RIGHT)
        aspect_lines[3].move_to(1.595*UP + 1.1*RIGHT)
        aspect_lines[4].move_to(1.905*UP + 1.1*RIGHT)
        
        self.play(Write(aspect_lines))

        self.wait(2)

        # Restore the state saved
        self.play(Restore(self.camera_frame))


    def show_opinions_example(self):
        background_rect = ScreenRectangle()
        background_rect.set_fill(WHITE, 1)
        background_rect.set_width(FRAME_WIDTH*1.2)
        background_rect.set_height(FRAME_HEIGHT*1.2)
        background = ImageMobject("img/opinion_photo.png")
        background.set_height(FRAME_HEIGHT)
        self.play(FadeIn(background_rect), FadeIn(background))
        # self.wait()
        
        opinion_rect = Rectangle(height=2.5, width=5.6)
        opinion_rect.set_color(BLUE_E)
        opinion_rect.move_to(1.10*UP + 0.1*RIGHT)
        opinion = TextMobject("Opinión")
        opinion.next_to(opinion_rect, 0.09*UP)
        opinion.set_color(BLUE_E)
        opinion.scale(0.6)

        # Entity inside Opinion Rectangle
        LINE_POSITION = 0.535*DOWN
        
        aspect_positive_rect = RoundedRectangle(width=1.485,height=0.23,corner_radius=0.05,stroke_width=0.7,color=GREEN_D,fill_color=GREEN_A,fill_opacity=0.25)
        aspect_positive_rect.move_to(opinion_rect)
        aspect_positive_rect.shift(LINE_POSITION + 1.4*LEFT)

        aspect_positive = TextMobject("Positiva")
        aspect_positive.set_stroke(width=1)
        aspect_positive.next_to(aspect_positive_rect, 0.001*DOWN)
        aspect_positive.set_color(GREEN_D)
        aspect_positive.scale(0.4)

        aspect_negative_rect = RoundedRectangle(width=1.665,height=0.23,corner_radius=0.05,stroke_width=0.7,color=RED_D,fill_color=RED_A,fill_opacity=0.25)
        aspect_negative_rect.move_to(opinion_rect)
        aspect_negative_rect.shift(LINE_POSITION + 0.46*RIGHT)

        aspect_negative = TextMobject("Negativa")
        aspect_negative.set_stroke(width=1)
        aspect_negative.next_to(aspect_negative_rect, 0.0001*DOWN)
        aspect_negative.set_color(RED_D)
        aspect_negative.scale(0.4)


        author = Line(0.45*LEFT, 0.45*RIGHT)
        author.set_color(GREY_BROWN)
        author.set_stroke(width=1.5)
        author.move_to(opinion_rect)
        author.shift(0.2*UP + 1.88*LEFT)

        author_txt = TextMobject("Autor")
        author_txt.next_to(author)
        author_txt.shift(0.65*LEFT + 0.1*UP)
        author_txt.set_color(GREY_BROWN)
        author_txt.scale(0.3)

        time = Line(0.5*LEFT, 0.85*RIGHT)
        time.set_color(GREY_BROWN)
        time.set_stroke(width=1.5)
        time.move_to(opinion_rect)
        time.shift(0.22*DOWN + 0.37*LEFT)

        time_txt = TextMobject("Tiempo")
        time_txt.next_to(time)
        time_txt.shift(0.82*LEFT + 0.08*UP)
        time_txt.set_color(GREY_BROWN)
        time_txt.scale(0.3)
  
        #End

        SENTIMENT_COLOR = YELLOW_E

        sentiment_rect = Rectangle(height=2.2, width=2.7)
        sentiment_rect.set_color(SENTIMENT_COLOR)
        sentiment_rect.move_to(2.7*UP + 5.3*LEFT)

        sentiment = TextMobject("Análisis de sentimientos")
        sentiment.next_to(sentiment_rect, 8.5*RIGHT)
        sentiment.shift(0.7*UP)
        sentiment.set_color(SENTIMENT_COLOR)
        sentiment.scale(0.6)

        sentiment_arrow = Arrow(sentiment_rect.get_right(), sentiment.get_left(), tip_length=0.15,buff=SMALL_BUFF)
        sentiment_arrow.set_stroke(width=1.4)
        # sentiment_arrow.scale(0.3)
        sentiment_arrow.set_color(SENTIMENT_COLOR)

        absa_rect = Rectangle(height=2.3, width=3)
        absa_rect.set_color(SENTIMENT_COLOR)
        absa_rect.move_to(5.15*LEFT)

        absa = TextMobject("Análisis de sentimientos basado en aspectos")
        absa.set_stroke(width=1)
        absa.next_to(absa_rect, 0.005*UP)
        absa.set_color(SENTIMENT_COLOR)
        absa.scale(0.34)

        all_rect = Rectangle(height=5.1, width=9.9)
        all_rect.set_color(BLACK)
        all_rect.move_to(1.35*UP + 1.9*LEFT)

        rects = VGroup(opinion_rect, sentiment_rect, absa_rect, all_rect)
        rects.set_stroke(width=2)
        
        big_rects = VGroup()
        for rect in rects:
            big_rect = FullScreenFadeRectangle(height=FRAME_HEIGHT*1.2, width=FRAME_WIDTH*1.2)
            rect.reverse_points()
            big_rect.append_vectorized_mobject(rect)
            big_rects.add(big_rect)


        self.play(Write(opinion), ShowCreation(rects[0]))

        self.camera_frame.save_state()
        saved_frame = self.camera_frame

        frame = self.camera_frame
        frame.generate_target()
        frame.target.scale(0.4)
        frame.target.move_to(rects[0])
        big_rect = big_rects[0].copy()

        self.play(
            FadeIn(big_rect),
            MoveToTarget(frame, run_time=1),
        )
        self.wait(5)

        # Display de aspectos
        self.play(Write(aspect_positive), ShowCreation(aspect_positive_rect))
        self.wait(5)
        self.play(Write(aspect_negative), ShowCreation(aspect_negative_rect))
        self.wait(5)

        # Display de autor y tiempo
        self.play(ShowCreation(author), Write(author_txt))
        self.wait()
        self.play(ShowCreation(time), Write(time_txt))
        self.wait(2)
        
        self.play(Restore(saved_frame))

        frame = saved_frame
        frame.generate_target()
        frame.target.scale(0.72)
        frame.target.move_to(rects[3])

        self.play(
            # Write(sentiment),
            # Write(absa),
            ShowCreation(rects[1]),
            # ShowCreation(rects[2]),
            MoveToTarget(frame, run_time=3),
            Transform(big_rect, big_rects[3]),
        )

        self.play(Write(sentiment), GrowArrow(sentiment_arrow))
        self.wait(3)

        self.play(Write(absa), ShowCreation(rects[2]))
        self.wait(2)

        self.play(FadeOut(big_rect), Restore(saved_frame))
        self.wait()


    def show_def_opinion(self):
        opinion=TexMobject(
            "(",
            "\\texttt{entidad}",
            ",",
            "\\texttt{aspecto}",
            ",",
            "\\texttt{polaridad}",
            ")",
            ",",
            "\\texttt{autor}",
            ",",
            "\\texttt{tiempo}",
            ")",
        )
        opinion.scale(1.2)
        self.play(Write(opinion[:6]),Write(opinion[7:]))

        entity_brace = Brace(opinion[1], UP, buff = SMALL_BUFF).set_color(BLUE)
        aspect_brace = Brace(opinion[3], UP, buff = SMALL_BUFF).set_color(GOLD)

        polarity_brace = Brace(opinion[5], UP, buff = SMALL_BUFF).set_color(GREEN)
        holder_brace = Brace(opinion[8], UP, buff = SMALL_BUFF)
        time_brace = Brace(opinion[10], UP, buff = SMALL_BUFF)

        entity_text = entity_brace.get_text("objeto de estudio")
        aspect_text = aspect_brace.get_text("características del objeto")

        polarity_text = polarity_brace.get_text("valoración del autor")
        holder_text = holder_brace.get_text("el que expresa la opinión")
        time_text = time_brace.get_text(r"tiempo de ingreso \\ al sistema")

        self.play(
            opinion[1].set_color, BLUE,
            GrowFromCenter(entity_brace),
            FadeIn(entity_text),
            )
        self.wait(1)

        self.play(
            opinion[3].set_color, GOLD,
        	ReplacementTransform(entity_brace,aspect_brace),
        	ReplacementTransform(entity_text,aspect_text)
        	)
        self.wait(2)

        self.play(
            opinion[5].set_color, GREEN,
        	ReplacementTransform(aspect_brace,polarity_brace),
        	ReplacementTransform(aspect_text,polarity_text)
        	)
        self.wait(2)

        self.play(
        	ReplacementTransform(polarity_brace,holder_brace),
        	ReplacementTransform(polarity_text,holder_text)
        	)
        self.wait(2)

        self.play(
        	ReplacementTransform(holder_brace,time_brace),
        	ReplacementTransform(holder_text,time_text)
        	)
        self.wait(2)

        self.play(FadeOut(time_brace), FadeOut(time_text))
        self.play(ReplacementTransform(opinion[7:], opinion[6]), run_time=1)
        self.play(LaggedStart(ApplyMethod(opinion[:7].shift, 2*RIGHT)), run_time=1)

        def_opinion_title=TextMobject("Definición de Opinión").scale(1.2).move_to(opinion[:7]).shift(UP)
        ul_def_opinion_title=underline(def_opinion_title, stroke_width=1)
        
        self.wait()

        self.play(
            Write(def_opinion_title),
            GrowFromCenter(ul_def_opinion_title),
        )
        self.wait()

        op_group = VGroup(def_opinion_title, ul_def_opinion_title, opinion[:7])

        self.play(op_group.to_edge, 0.8*UP)

        self.wait()

        def_obj_title=TextMobject("Objetivo").scale(1.2).next_to(op_group, 5*DOWN)
        ul_def_obj_title=underline(def_obj_title, stroke_width=1)

        obj_text = TextMobject("Recuperar las opiniones en los textos de forma automática.").next_to(def_obj_title, 1.5*DOWN)

        def_sol_title=TextMobject("Solución Propuesta").scale(1.2).next_to(obj_text, 5.1*DOWN)
        ul_def_sol_title=underline(def_sol_title, stroke_width=1)

        sol_text = TextMobject('Utilizar "Métodos de ', 'Aprendizaje Automático', '".').next_to(def_sol_title, 1.5*DOWN)
        red_text = TextMobject('En particular ', '"', 'Redes Neuronales Artificiales', '".').next_to(sol_text, 0.2*DOWN)

        self.play(
            Write(def_obj_title),
            GrowFromCenter(ul_def_obj_title),
        )
        self.wait(2)

        self.play(Write(obj_text))
        self.play(
            Write(def_sol_title),
            GrowFromCenter(ul_def_sol_title),
        )
        self.play(Write(sol_text))
        self.play(Write(red_text))
        self.wait(2)

        self.play(
            FadeOut(op_group),
            FadeOut(def_obj_title),
            FadeOut(ul_def_obj_title),
            FadeOut(obj_text),
        )

        self.def_sol_title = def_sol_title
        self.ul_def_sol_title = ul_def_sol_title
        self.sol_text = sol_text
        self.red_text = red_text


    def add_title(self, text):
        title = TextMobject(text)
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(4)
        h_line.next_to(title, DOWN)
        self.h_line = h_line
        self.title = title
        self.play(Write(title), Write(h_line))

    def show_words(self):
        words = VGroup(
            TextMobject("Aprendizaje", " Automático").set_color(BLUE_C),
            TextMobject("Red Neuronal Artificial").set_color(BLUE_D),
        )
        
        words.arrange(DOWN)
        words.to_corner(UR,buff=0.3)
        self.play(
            FadeOut(self.def_sol_title),
            FadeOut(self.ul_def_sol_title),
            FadeOut(self.sol_text),
            FadeOut(self.red_text),
            ReplacementTransform(self.sol_text[1].copy(), words[0]),
            ReplacementTransform(self.red_text[2].copy(), words[1])
        )
        self.wait()

        self.words = words

    def show_network(self):
        network_mob = self.network_mob
        network_mob.shift(0.4*DOWN)
        self.play(
            ReplacementTransform(
                VGroup(self.words[1]),
                network_mob.layers
            ),
            run_time = 1
        )
        self.play(ShowCreation(
            network_mob.edge_groups,
            lag_ratio = 0.5,
            run_time = 3,
            rate_func=linear,
        ))

        self.wait(3)
        # in_vect = np.random.random(self.network.sizes[0])
        # self.feed_forward(in_vect)

    def get_document(self):
        lines = VGroup(*[Line(LEFT, RIGHT) for x in range(5)])
        lines.arrange(DOWN)
        last_line = lines[-1]
        last_line.scale(0.7, about_point = last_line.get_left())

        signature_line = lines[0].copy()
        signature_line.set_stroke(width = 2)
        signature_line.next_to(lines, DOWN, LARGE_BUFF)
        ex = TexMobject("\\times")
        ex.scale(0.7)
        ex.next_to(signature_line, UP, SMALL_BUFF, LEFT)
        lines.add(ex, signature_line)

        rect = SurroundingRectangle(
            lines, 
            color = LIGHT_GREY, 
            buff = MED_SMALL_BUFF
        )

        text = TextMobject("Texto")
        # text.scale(0.7)
        text.next_to(rect, UP, 0.3)
        
        opinion=TexMobject(
            "\\texttt{entidad}",
            ",",
            "\\texttt{aspecto}",
        )
        opinion[0].set_color(BLUE)
        opinion[2].set_color(GOLD)
        opinion.next_to(rect, DOWN, 0.3)
        opinion.scale(0.85)


        document = VGroup(rect, lines, text, opinion)
        # signature = get_cursive_name("Texto")
        # signature.set_color(self.signature_color)
        # line = document[1][-1]
        # signature.next_to(line, UP, SMALL_BUFF)
        return document

    def show_input_document(self):
        document = self.get_document()
        document.to_edge(LEFT)
        #document.scale(0.7)
        document.shift(0.5*UP + 0.85*RIGHT)
        document_copy = document.copy()

        network_mob = self.network_mob
        layers = network_mob.layers
        layers.save_state()

        input_layer = layers[0]
        all_edges = VGroup(*it.chain(*network_mob.edge_groups))
        
        self.play(ShowCreation(document), ShowCreation(document_copy), run_time=2)
        self.wait(2)
        
        edge_animation = LaggedStartMap(
            ShowCreationThenDestruction, 
            all_edges.copy().set_fill(YELLOW).set_color(YELLOW).set_stroke(width=1.8),
            run_time = 2.5,
            lag_ratio = 0.05,
            remover = True,
            rate_func=linear,
        )
        
        layer_animation = Transform(
            # VGroup(*layers), VGroup(*active_layers),
            document_copy, input_layer,
            run_time = 1.5,
            # lag_ratio = 0.5,
            rate_func=linear,
        )
        self.play(layer_animation)
        self.play(edge_animation)
        # self.wait()

        self.document = document

    def show_output_layer(self):
        text_labels = ['Positivo', 'Neutral', 'Negativo']
        text_color = [GREEN, WHITE, RED]
        labels = VGroup()
        neurons = self.network_mob.layers[-1].neurons
        labels_height = [0.225, 0.22, 0.25]
        for i in range(3):
            neuron = neurons[i]
            label = TexMobject(text_labels[i], stroke_width=0.5, color=text_color[i])
            label.set_height(labels_height[i])
            label.move_to(neuron)
            label.shift(0.75*RIGHT)
            labels.add(label)
        
        layer = self.network_mob.layers[-1]
        rect = SurroundingRectangle(
            VGroup(layer, labels)
        )
        neuron = layer.neurons[0]
        neuron.set_fill(GREEN, 0)
        label = labels[0]
        print(str(label))
        for mob in neuron, label:
            mob.save_state()
            mob.generate_target()
        neuron.target.scale_in_place(4)
        neuron.target.shift(1.5*RIGHT)
        label.target.scale(1.5)
        label.target.next_to(neuron.target, RIGHT)

        activation = DecimalNumber(0)
        activation.move_to(neuron.target)

        def change_activation(num):
            self.play(
                neuron.set_fill, None, num,
                ChangingDecimal(
                    activation,
                    lambda a : neuron.get_fill_opacity(),
                ),
                UpdateFromFunc(
                    activation,
                    lambda m : m.set_fill(
                        BLACK if neuron.get_fill_opacity() > 0.8 else WHITE
                    )
                ),
                run_time=0.5,
            )

        self.play(ShowCreation(rect), run_time=1)
        self.play(LaggedStartMap(FadeIn, labels), run_time=1)
        self.wait()
        self.play(
            MoveToTarget(neuron),
            MoveToTarget(label),
            FadeOut(rect),
        )
        self.play(FadeIn(activation))
        
        for num in 0.1, 0.97:
            change_activation(num)
            self.wait()
        self.wait(2)

        self.play(
            neuron.restore,
            neuron.set_fill, None, 1,
            label.restore,
            FadeOut(activation),
        )
        self.wait()

        self.labels = labels

    def show_learning(self):
        word = self.words[0][0].copy()
        rect = SurroundingRectangle(word, color = YELLOW)
        self.network_mob.neuron_fill_color = GREEN_E

        layer = self.network_mob.layers[-1]
        activation = np.zeros(len(layer.neurons))
        activation[0] = 1.0
        active_layer = self.network_mob.get_active_layer(
            -1, activation
        )
        word_group = VGroup(word, rect)
        word_group.generate_target()
        word_group.target.to_edge(LEFT)
        word_group.target[0].set_color(YELLOW)
        word_group.target[1].set_stroke(width = 0)

        self.play(ShowCreation(rect))
        self.play(
            Transform(layer, active_layer),
            MoveToTarget(word_group),
        )

        for edge_group in reversed(self.network_mob.edge_groups):
            m = 2
            edge_group.generate_target()
            for edge in edge_group.target:
                edge.set_stroke(
                    YELLOW, 
                    width = (4*np.random.random()**2) + m
                )
                edge.set_color_by_gradient([GREEN, RED, YELLOW])
                if m > 0:
                    m = -1
            self.play(MoveToTarget(edge_group))
            

        signature = get_cursive_name("Positivo")
        signature.set_color(GREEN)
        line = self.document[1][-1]
        signature.next_to(line, UP, SMALL_BUFF)
        self.play(Write(signature))
        self.wait(2)

        absa=TextMobject("Análisis de sentimientos basado en aspectos").to_corner(UP)
        absa_ul=underline(absa, stroke_width=1)

        self.play(
            ReplacementTransform(self.words, absa),
            Write(absa_ul),
            FadeOut(word),
        ) 

        self.wait(4)
        self.learning_word = word

    def show_benefit(self):
        titulo=TextMobject("¿Para qué sirve el estudio de las opiniones?").scale(1.2).to_edge(UP).shift(UP*0.25)
        ul=underline(titulo)
        ul.set_stroke(width=1)
        lista=VGroup(
            TextMobject("$\\bullet$ Organiza la información más eficiente."),
            TextMobject("$\\bullet$ Entender rápidamente actitudes del consumidor y reaccionar."),
            TextMobject("$\\bullet$ Contribuye en la toma de decisiones."),
            TextMobject("$\\bullet$ Facilita el conocimiento de los usuarios de una empresa."),
            TextMobject("$\\bullet$ Desarrollar estrategias atraer nuevos clientes."),
            TextMobject("$\\bullet$ Herramientas visuales."),
            TextMobject("$\\bullet$ Método para realizar encuestas rápidas."),
            TextMobject("$\\bullet$ Marketing personalizado: Ofrecer productos para audiencias específicas."),
            ).arrange_submobjects(DOWN,aligned_edge=LEFT)

        lista.scale(0.8)
        lista.next_to(titulo, 4.5*DOWN)

        self.play(Write(titulo),GrowFromCenter(ul))
        self.play(LaggedStart(Write(lista)))
        self.wait(9)
        self.play(
            FadeOut(titulo),
            FadeOut(ul),
            FadeOut(lista),
            run_time=1,
        )
        self.wait()
        

    def show_end(self):
        confetti_spirils = self.confetti_spirils = list(map(
            turn_animation_into_updater,
            get_confetti_animations(100)
        ))
        self.add(*confetti_spirils)
        self.play(ShowCreation(TextMobject("¡Muchas Gracias!").scale(1.5)), run_time=2)
        self.wait(3)


def get_cursive_name(name):
    result = TextMobject("\\normalfont\\calligra %s"%name)
    result.set_stroke(width = 0.4)
    return result