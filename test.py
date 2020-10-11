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
from nn.network import *


class ZoomedScene(MovingCameraScene):
    CONFIG = {
        "camera_class": MultiCamera,
        "zoomed_display_height": 3,
        "zoomed_display_width": 3,
        "zoomed_display_center": None,
        "zoomed_display_corner": UP + RIGHT,
        "zoomed_display_corner_buff": DEFAULT_MOBJECT_TO_EDGE_BUFFER,
        "zoomed_camera_config": {
            "default_frame_stroke_width": 2,
            "background_opacity": 1,
        },
        "zoomed_camera_image_mobject_config": {},
        "zoomed_camera_frame_starting_position": ORIGIN,
        "zoom_factor": 0.15,
        "image_frame_stroke_width": 3,
        "zoom_activated": False,
    }

    def setup(self):
        MovingCameraScene.setup(self)
        # Initialize camera and display
        zoomed_camera = MovingCamera(**self.zoomed_camera_config)
        zoomed_display = ImageMobjectFromCamera(
            zoomed_camera, **self.zoomed_camera_image_mobject_config
        )
        zoomed_display.add_display_frame()
        for mob in zoomed_camera.frame, zoomed_display:
            mob.stretch_to_fit_height(self.zoomed_display_height)
            mob.stretch_to_fit_width(self.zoomed_display_width)
        zoomed_camera.frame.scale(self.zoom_factor)

        # Position camera and display
        zoomed_camera.frame.move_to(self.zoomed_camera_frame_starting_position)
        if self.zoomed_display_center is not None:
            zoomed_display.move_to(self.zoomed_display_center)
        else:
            zoomed_display.to_corner(
                self.zoomed_display_corner,
                buff=self.zoomed_display_corner_buff
            )

        self.zoomed_camera = zoomed_camera
        self.zoomed_display = zoomed_display

    def activate_zooming(self, animate=False):
        self.zoom_activated = True
        self.camera.add_image_mobject_from_camera(self.zoomed_display)
        if animate:
            self.play(self.get_zoom_in_animation())
            self.play(self.get_zoomed_display_pop_out_animation())
        self.add_foreground_mobjects(
            self.zoomed_camera.frame,
            self.zoomed_display,
        )

    def get_zoom_in_animation(self, run_time=2, **kwargs):
        frame = self.zoomed_camera.frame
        full_frame_height = self.camera.get_frame_height()
        full_frame_width = self.camera.get_frame_width()
        frame.save_state()
        frame.stretch_to_fit_width(full_frame_width)
        frame.stretch_to_fit_height(full_frame_height)
        frame.center()
        frame.set_stroke(width=0)
        return ApplyMethod(frame.restore, run_time=run_time, **kwargs)

    def get_zoomed_display_pop_out_animation(self, **kwargs):
        display = self.zoomed_display
        display.save_state(use_deepcopy=True)
        display.replace(self.zoomed_camera.frame, stretch=True)
        return ApplyMethod(display.restore)

    def get_zoom_factor(self):
        return fdiv(
            self.zoomed_camera.frame.get_height(),
            self.zoomed_display.get_height()
        )


def rango(v_in,v_fin,step=1):
    return list(np.arange(v_in,v_fin+step,step))

def direcciones_v1(text):
	direccion=[]
	for i in range(len(text)):
		if i%2!=0 and i!=0 and i!=len(text)-1:
			direccion.append(UP*0.5)
		elif i%2==0 and i!=0 and i!=len(text)-1:
			direccion.append(DOWN*0.5)
		elif i==0:
			direccion.append(LEFT)
		elif i==len(text)-1:
			direccion.append(RIGHT)
	return direccion
def direcciones_v2(text):
	direccion=[]
	for i in range(len(text)):
		direccion.append(UP*(len(text)-i)/len(text)*1.8)
	return direccion
def direcciones_v3(text):
	direccion=[]
	for i in range(len(text)):
		direccion.append(UP*(i)/len(text))
	return direccion

def coord(x,y):
	return np.array([x,y,0])


def TypeWriter_(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,end=False):
    def devuelve_random():
        return random.randint(1,5)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("typewriter/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("typewriter/enter")
            self.wait(time_spaces)

        self.add_sound("typewriter/tecla%s"%devuelve_random())
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i==len(texto)-1 and end==True:
            self.add_sound("typewriter/fin")
            self.wait(0.1*devuelve_random()*time_random)

def TypeWriter(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,end=False):
    def devuelve_random():
        return random.randint(1,3)
    for i in range(len(texto)):

        self.add_sound("typewriter/tecla%s"%devuelve_random())
        texto[i].set_fill(None,1)
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i<len(texto)-1:
            pre_ty=texto[i].get_center()[1]
            pre_tx=texto[i].get_center()[0]
            pos_ty=texto[i+1].get_center()[1]
            pos_tx=texto[i+1].get_center()[0]
            pre_width=texto[i].get_width()/2
            pos_width=texto[i+1].get_width()/2
            pre_height=texto[i].get_height()/2
            pos_height=texto[i+1].get_height()/2
            dist_min_x=(pre_width+pos_width)*1.6
            dist_min_y=(pre_height+pos_height)*1.2
            if i==0 or dist_max_x<dist_min_x:
                dist_max_x=dist_min_x
            if i==0 or dist_max_y<dist_min_y:
                dist_max_y=dist_min_y
            if abs(pre_ty-pos_ty)>dist_max_y:
                self.add_sound("typewriter/enter")
                self.wait(time_spaces)
            elif abs(pre_tx-pos_tx)>dist_max_x and abs(pre_ty-pos_ty)<dist_max_y:
                self.add_sound("typewriter/espacio")
                self.wait(time_spaces)
        if i==len(texto)-1:
            self.add_sound("typewriter/enter")
            self.wait(time_spaces)

def KeyBoard_(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25):
    def devuelve_random():
        return random.randint(1,3)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("computer_keyboard/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)
        self.add_sound("computer_keyboard/tecla%s"%devuelve_random())
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i==len(texto)-1:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)


def KeyBoard(self,texto,p=0.037,lag=0.037,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25):
    def devuelve_random():
        return random.randint(1,3)
    for i in range(len(texto)):

        self.add_sound("computer_keyboard/tecla%s"%devuelve_random())
        texto[i].set_fill(None,1)
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i<len(texto)-1:
            pre_ty=texto[i].get_center()[1]
            pre_tx=texto[i].get_center()[0]
            pos_ty=texto[i+1].get_center()[1]
            pos_tx=texto[i+1].get_center()[0]
            pre_width=texto[i].get_width()/2
            pos_width=texto[i+1].get_width()/2
            pre_height=texto[i].get_height()/2
            pos_height=texto[i+1].get_height()/2
            dist_min_x=(pre_width+pos_width)*1.6
            dist_min_y=(pre_height+pos_height)*1.2
            if i==0 or dist_max_x<dist_min_x:
                dist_max_x=dist_min_x
            if i==0 or dist_max_y<dist_min_y:
                dist_max_y=dist_min_y
            if abs(pre_ty-pos_ty)>dist_max_y:
                self.add_sound("computer_keyboard/enter")
                self.wait(time_spaces)
            elif abs(pre_tx-pos_tx)>dist_max_x and abs(pre_ty-pos_ty)<dist_max_y:
                self.add_sound("computer_keyboard/espacio")
                self.wait(time_spaces)
        if i==len(texto)-1:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)
		
def escribe_texto(self,texto,tiempo_texto=1.1,escala_linea=1.5,buff_linea=0.2,**kwargs):
    linea_guia=Line(texto.get_corner(UL),texto.get_corner(DL)).shift(LEFT*buff_linea).scale(escala_linea)
    grupo_lineas=VGroup()
    for letter in texto:
        linea = Line(letter.get_top(),letter.get_bottom())
        linea.replace(letter, dim_to_match=1)
        linea.fade(1)
        linea.save_state()
        grupo_lineas.add(linea)
        linea.target = letter

    coord1=texto.get_right()+RIGHT*buff_linea
    coord2=linea.get_center()
    coordf=np.array([coord1[0],coord1[1],0])
    self.play(FadeIn(linea_guia))
    # self.play(LaggedStart(MoveToTarget,grupo_lineas,run_time=tiempo_texto),linea_guia.move_to,coordf,**kwargs)
    self.play(FadeOut(linea_guia))
    return grupo_lineas

def reescribe_texto(self,texto_i,texto,tiempo_pre_texto=1.1,tiempo_pos_texto=1.1,escala_linea=1.5,buff_linea=0.2,alineacion=UL,**kwargs):
    texto.move_to(texto_i,aligned_edge=alineacion)
    linea_guia=Line(texto.get_corner(UL),texto.get_corner(DL)).shift(LEFT*buff_linea).scale(escala_linea)
    grupo_lineas=VGroup()
    for letter in texto:
        linea = Line(letter.get_top(),letter.get_bottom())
        linea.replace(letter, dim_to_match=1)
        linea.fade(1)
        linea.save_state()
        grupo_lineas.add(linea)
        linea.target = letter
    if texto.get_width()<texto_i.get_width():
        texto_ref=texto_i
    else:
        texto_ref=texto
    coord1=texto_ref.get_right()+RIGHT*buff_linea
    coord2=linea.get_center()
    coordf=np.array([coord1[0],coord1[1],0])
    self.play(FadeIn(linea_guia))
    self.play(FadeOut(linea_guia))
    return grupo_lineas

def seleccion_texto(self,texto,color=YELLOW,proporcion_h=1.2,proporcion_w=1.2,opacidad=0.7,direccion=LEFT):
    texto.rect=Rectangle(width=0.001,height=texto.get_height()*proporcion_h).set_fill(color).fade(opacidad).set_stroke(None,0)
    texto.pos_rect=Rectangle(width=texto.get_width()*proporcion_w,height=texto.get_height()*proporcion_h).set_fill(color).fade(opacidad).set_stroke(None,0)
    texto.pos_rect.move_to(texto)
    texto.rect.next_to(texto.pos_rect,direccion,buff=0)

def mostrar_seleccion_texto(self,texto):
    return Transform(texto.rect,texto.pos_rect)

def seleccion_grande_texto(self,texto,escala=1.1,color=YELLOW,opacidad=0.7):
    rectg=Rectangle(width=FRAME_X_RADIUS*2,height=texto.get_height()*escala).set_fill(color).fade(opacidad).set_stroke(None,0)
    rectg.move_to(ORIGIN)
    coord_x=rectg.get_center()[0]
    coord_y=texto.get_center()[1]
    rectg.move_to(np.array([coord_x,coord_y,0]))
    return rectg

def mueve_seleccion(self,rectg,objeto,**kwargs):
    rectg.generate_target()
    coord_x=rectg.get_center()[0]
    coord_y=objeto.get_center()[1]
    rectg.target.move_to(np.array([coord_x,coord_y,0]))
    self.play(MoveToTarget(rectg),**kwargs)

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


class underline(Line):
    # buff 0.07
    def __init__(self,texto,buff=0.09,**kwargs):
        Line.__init__(self,texto.get_corner(DL),texto.get_corner(DR),**kwargs)
        self.shift(DOWN*buff)



class Test(MovingCameraScene):
    def construct(self):
        step1 = TextMobject("Step 1")
        step2 = TextMobject("Step 2")
        step1.move_to(LEFT*2+DOWN*2)
        step2.move_to(4*RIGHT+2*UP)
        arrow1 = Arrow(step1.get_right(),step2.get_left(),buff=0.1)
        arrow1.set_color(RED)
        arrow2 = Arrow(step1.get_top(),step2.get_bottom(),buff=0.1)
        arrow2.set_color(BLUE)
        self.play(Write(step1),Write(step2))
        self.play(GrowArrow(arrow1))
        self.play(GrowArrow(arrow2))
        self.wait()


class MainPresentation(MovingCameraScene):
    CONFIG = {
        "public_color" : GREEN,
        "private_color" : RED,
        "signature_color" : BLUE_C,
    }

    def construct(self):
        # self.show_quote()
        # self.remove_all_obj_in_scene()
        # self.show_title()
        # self.introduction()
        # self.remove_all_obj_in_scene()
        # self.show_amazon_example()
        # self.remove_all_obj_in_scene()
        # self.show_opinions_example()
        # self.remove_all_obj_in_scene()
        # self.show_def_opinion()
        # self.remove_all_obj_in_scene()
        #self.add_title('Nuevo titulo principal')
        self.test()

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

        self.play(FadeIn(words), run_time=2.5)
        self.wait(1)
        self.play(Write(author, run_time = 4))
        self.wait(2)

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
                run_time=2)
            self.wait(1)
            self.play(
                FadeOut(universidad),
                FadeOut(facultad),
                FadeOut(title),
                FadeOut(autor),
                FadeOut(instituto),
                FadeOut(grupo),
            )
            self.wait(2)
    
    def introduction(self):
            question_1 = TextMobject('¿Que entendemos por ','"', 'Opinión', '"?')
            question_2 = TextMobject('¿Como definimos la "', 'Opinion', r'" de forma en que \\ una computadora lo entienda?')
            question_2[1].set_color(YELLOW)
            self.play(Write(question_1))
            self.play(question_1[2].set_color, YELLOW)
            self.wait()

            self.play(ReplacementTransform(question_1, question_2))
            self.wait(3)


    def show_amazon_example(self):
        background = ImageMobject("img/celular_amazon.png")
        background.set_height(FRAME_HEIGHT)
        self.play(FadeIn(background))
        self.wait(1)

        entity_rect = Rectangle(height=5.3, width=2.6)
        entity_rect.move_to(0.4*UP + 3.55*LEFT)
        entity = TextMobject("Entidad")
        entity.next_to(entity_rect, 0.3*UP)
        VGroup(entity, entity_rect).set_color(BLUE_E)

        self.play(ShowCreation(entity_rect), run_time=2)
        self.play(
            Write(entity),
        )
        self.wait(1)

        aspect_rect = Rectangle(height=2.56, width=4)
        aspect_rect.move_to(0.9*UP + 1.5*RIGHT)
        aspect = TextMobject("Aspectos")
        aspect.next_to(aspect_rect, 0.3*UP)
        aspect_group = VGroup(aspect, aspect_rect).set_color(GREEN_E)

        self.play(ShowCreation(aspect_rect), run_time=2)
        self.play(
            Write(aspect),
        )

        self.wait(2)

        # Save the state of camera
        self.camera_frame.save_state()

        # Animation of the camera
        self.play(
            # Set the size with the width of a object
            self.camera_frame.set_height,aspect_group.get_height()*1.2,
            # Move the camera to the object
            self.camera_frame.move_to,aspect_group
        )
        self.wait(2)
        
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

        self.wait()

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
        self.wait()
        
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

        sentiment_arrow = Arrow(sentiment_rect.get_right(),sentiment.get_left(), tip_length=0.15,buff=SMALL_BUFF)
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
            MoveToTarget(frame, run_time=3),
        )
        self.wait()

        # Display de autor y tiempo

        self.play(ShowCreation(author), Write(author_txt))
        self.play(ShowCreation(time), Write(time_txt))
        
        # Display de aspectos
        self.play(Write(aspect_positive), ShowCreation(aspect_positive_rect))
        self.play(Write(aspect_negative), ShowCreation(aspect_negative_rect))
        self.wait()
        
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
        self.wait()

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
        # opinion[1].set_color(BLUE)
        # opinion[3].set_color(GOLD)
        self.play(Write(opinion[:6]),Write(opinion[7:]))

        entity_brace = Brace(opinion[1], UP, buff = SMALL_BUFF).set_color(BLUE)
        aspect_brace = Brace(opinion[3], UP, buff = SMALL_BUFF).set_color(GOLD)

        polarity_brace = Brace(opinion[5], UP, buff = SMALL_BUFF).set_color(GREEN)
        holder_brace = Brace(opinion[8], UP, buff = SMALL_BUFF)
        time_brace = Brace(opinion[10], UP, buff = SMALL_BUFF)

        entity_text = entity_brace.get_text("objeto de estudio")
        aspect_text = aspect_brace.get_text("caracteristica del objeto")

        polarity_text = polarity_brace.get_text("valoracion del autor")
        holder_text = holder_brace.get_text("el que expresa la opinion")
        time_text = time_brace.get_text(r"tiempo de ingreso \\ al sistema")

        self.play(
            opinion[1].set_color, BLUE,
            GrowFromCenter(entity_brace),
            FadeIn(entity_text),
            )
        self.wait()

        self.play(
            opinion[3].set_color, GOLD,
        	ReplacementTransform(entity_brace,aspect_brace),
        	ReplacementTransform(entity_text,aspect_text)
        	)
        self.wait()

        self.play(
            opinion[5].set_color, GREEN,
        	ReplacementTransform(aspect_brace,polarity_brace),
        	ReplacementTransform(aspect_text,polarity_text)
        	)
        self.wait()

        self.play(
        	ReplacementTransform(polarity_brace,holder_brace),
        	ReplacementTransform(polarity_text,holder_text)
        	)
        self.wait()

        self.play(
        	ReplacementTransform(holder_brace,time_brace),
        	ReplacementTransform(holder_text,time_text)
        	)
        self.wait()

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

        obj_text = TextMobject("Recuperar las opiniones en los textos.").next_to(def_obj_title, 1.5*DOWN)

        def_sol_title=TextMobject("Solucion Propuesta").scale(1.2).next_to(obj_text, 5.5*DOWN)
        ul_def_sol_title=underline(def_sol_title, stroke_width=1)

        sol_text = TextMobject('Utilizar "Metodos de Aprendizaje Automatico".').next_to(def_sol_title, 1.5*DOWN)

        self.play(
            Write(def_obj_title),
            GrowFromCenter(ul_def_obj_title),
        )
        self.play(Write(obj_text))
        self.play(
            Write(def_sol_title),
            GrowFromCenter(ul_def_sol_title),
        )
        self.play(Write(sol_text))
        self.wait()

    def add_title(self, text):
        title = TextMobject(text)
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(4)
        h_line.next_to(title, DOWN)
        self.h_line = h_line
        self.title = title
        self.play(Write(title), Write(h_line))


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
        document = VGroup(rect, lines)
        signature = get_cursive_name("Texto")
        signature.set_color(self.signature_color)
        line = document[1][-1]
        signature.next_to(line, UP, SMALL_BUFF)
        """
        documents = VGroup(*[
            document.copy()
            for x in range(2)
        ])
        documents.arrange(RIGHT, buff = MED_LARGE_BUFF)
        documents.to_corner(UP+LEFT)

        signatures = VGroup()
        for document in documents:
            signature = get_cursive_name("Texto 1")
            signature.set_color(self.signature_color)
            line = document[1][-1]
            signature.next_to(line, UP, SMALL_BUFF)
            signatures.add(signature)

        self.play(
            # FadeOut(self.title),
            # FadeOut(self.h_line),
            LaggedStartMap(FadeIn, documents, run_time = 1)
        )
        self.play(Write(signatures))
        self.wait()
        self.signatures = signatures
        self.documents = documents
        """
        return VGroup(document, signature)
        
    def test(self):
        print(sys.path)
        rect = Rectangle(
            height = 2.5, width = 7,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        self.play(ShowCreation(rect))
        self.wait()


    def test2(self):
        document = self.get_document()
        rect = Rectangle(
            height = 2.5, width = 7,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        #rect.to_corner(UP+LEFT, buff = 0)
        rect.stretch_to_fit_height(FRAME_HEIGHT)
        # rect.move_to(self.corner_rect.get_bottom(), UP)

        h_line = Line(rect.get_left(), rect.get_right())
        h_line.next_to(rect.get_top(), DOWN, LARGE_BUFF)
        
        v_line = Line(rect.get_top(), rect.get_bottom())
        v_line.shift(2*LEFT)
        v_line.set_color(BLUE)

        v2_line = Line(rect.get_top(), rect.get_bottom())
        v2_line.shift(RIGHT)
        
        uv_title = TexMobject("(u, v)")
        triple_title = TexMobject("(u^2 - v^2)")
        triple_title2 = TexMobject("(u^3 - v^3)")
        
        uv_title.scale(0.75)
        triple_title.scale(0.75)
        triple_title2.scale(0.75)
        
        uv_title.next_to(
            h_line.point_from_proportion(0.1), 
            UP, SMALL_BUFF
        )
        triple_title.next_to(
            h_line.point_from_proportion(0.45),
            UP, SMALL_BUFF
        )

        triple_title2.next_to(
            h_line.point_from_proportion(0.85),
            UP, SMALL_BUFF
        )

        pairs = [(2, 1), (3, 2)]
        pair_mobs = VGroup()
        triple_mobs = VGroup()
        new_mobs = VGroup()
        for u, v in pairs:
            a, b, c = u**2 - v**2, 2*u*v, u**2 + v**2
            pair_mob = TexMobject("(", str(u), ",", str(v), ")")
            pair_mob.set_color_by_tex(str(u), GREEN)
            pair_mob.set_color_by_tex(str(v), RED)
            new_mob = document.copy()
            triple_mob = TexMobject("(%d, %d, %d)"%(a, b, c))
            pair_mobs.add(pair_mob)
            new_mobs.add(new_mob)
            triple_mobs.add(triple_mob)
            pair_mob.scale(0.75)
            triple_mob.scale(0.75)
            new_mob.scale(0.4)
        pair_mobs.arrange(DOWN)
        pair_mobs.next_to(uv_title, 1.5*DOWN, MED_LARGE_BUFF)
        triple_mobs.arrange(DOWN)
        triple_mobs.next_to(triple_title, 1.5*DOWN, MED_LARGE_BUFF)
        new_mobs.arrange(DOWN)
        new_mobs.next_to(triple_title2, DOWN, MED_LARGE_BUFF)

        self.play(*list(map(FadeIn, [
            rect, h_line, v_line, v2_line, 
            uv_title, triple_title, triple_title2
        ])))
        self.play(*[
            LaggedStartMap(
                FadeIn, mob, 
                run_time = 2,
                lag_ratio = 0.2
            )
            for mob in (pair_mobs, triple_mobs, new_mobs)
        ])


def get_cursive_name(name):
    result = TextMobject("\\normalfont\\calligra %s"%name)
    result.set_stroke(width = 0.4)
    return result

class ZoomT2(ZoomedScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
        "zoom_factor": 0.3,
        "zoomed_display_height": 1,
        "zoomed_display_width": 6,
    }

    def show_temario(self):
        titulo=TextMobject("\\sc Temario").scale(2).to_edge(UP).shift(UP*0.25)
        ul=underline(titulo)
        lista=VGroup(
            TextMobject("0. Instalación (Windows, Mac, GNU/Linux)."),
            TextMobject("1. Formato de textos."),
            TextMobject("2. Fórmulas en \\TeX."),
            TextMobject("3. Arreglos."),
            TextMobject("4. Transformaciones."),
            TextMobject("5. Herramientas visuales."),
            TextMobject("6. Introducción a las gráficas 2D."),
            TextMobject("7. Introducción a las gráficas 3D."),
            TextMobject("8. Agregar audio."),
            TextMobject("9. Insertar imágenes y SVGs."),
            TextMobject("10. Primer proyecto.")
            ).arrange_submobjects(DOWN,aligned_edge=LEFT).next_to(titulo,DOWN,buff=0.1).scale(0.87)

        self.play(Write(titulo),GrowFromCenter(ul))
        self.play(LaggedStart(Write(lista)))
        self.wait()

        
    def setup(self):
        ZoomedScene.setup(self)

    def construct(self):
        # grilla=Grilla()
        #self.add_foreground_mobject(grilla)
        texto1=Texto("Undolatory theory",color=RED)
        texto2=Texto("Experimento de Airy",color=PURPLE)

        conj_texto1=VGroup(texto1,texto2)
        conj_texto1.arrange_submobjects(DOWN,aligned_edge=LEFT)



        imagen=ImageMobject("img/iphone.png")
        imagen.set_height(7)
        imagen.shift(LEFT*3)
        self.add(imagen)

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame

        frame.move_to(3.05 * LEFT + 1.4 * UP)
        frame.set_color(WHITE)

        zoomed_display.display_frame.set_color(WHITE)

        zd_rect = BackgroundRectangle(
            zoomed_display,
            fill_opacity=0,
            buff=MED_SMALL_BUFF,
        )

        self.add_foreground_mobject(zd_rect)

        zd_rect.anim = UpdateFromFunc(
            zd_rect,
            lambda rect: rect.replace(zoomed_display).scale(1.1)
        )
        #zd_rect.next_to(FRAME_HEIGHT * RIGHT, UP)

        zoomed_display.move_to(ORIGIN+RIGHT*3+UP*3)

        conj_texto1.next_to(zoomed_display,DOWN)

        self.play(ShowCreation(frame))
        self.activate_zooming()
        #'''
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim
        )
        self.play(Write(texto1))
        #'''
        self.wait()
        '''
        self.play(
            #self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        #'''
        print("aqui")
        self.play(
            frame.scale,[0.5,1.5,1],
            zoomed_display.scale,[0.5,1.5,1],
            zoomed_display.display_frame.scale,[0.5,1.5,1],
            )
        self.play(
            frame.scale,1.5,
            frame.shift,2.5*DOWN
            )

        self.wait()
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        self.play(
            zoomed_display.display_frame.fade,1,
            frame.fade,1
            )
        self.wait()


class ZoomT(ZoomedScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
        "zoom_factor": 0.3,
        "zoomed_display_height": 1,
        "zoomed_display_width": 6,
    }

    def setup(self):
        ZoomedScene.setup(self)

    def construct(self):
        # grilla=Grilla()
        #self.add_foreground_mobject(grilla)
        texto1=Texto("Undolatory theory",color=RED)
        texto2=Texto("Experimento de Airy",color=PURPLE)

        conj_texto1=VGroup(texto1,texto2)
        conj_texto1.arrange_submobjects(DOWN,aligned_edge=LEFT)



        imagen=ImageMobject("img/iphone.png")
        imagen.set_height(7)
        imagen.shift(LEFT*3)
        self.add(imagen)

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame

        frame.move_to(3.05 * LEFT + 1.4 * UP)
        frame.set_color(WHITE)

        zoomed_display.display_frame.set_color(WHITE)

        zd_rect = BackgroundRectangle(
            zoomed_display,
            fill_opacity=0,
            buff=MED_SMALL_BUFF,
        )

        self.add_foreground_mobject(zd_rect)

        zd_rect.anim = UpdateFromFunc(
            zd_rect,
            lambda rect: rect.replace(zoomed_display).scale(1.1)
        )
        #zd_rect.next_to(FRAME_HEIGHT * RIGHT, UP)

        zoomed_display.move_to(ORIGIN+RIGHT*3+UP*3)

        conj_texto1.next_to(zoomed_display,DOWN)

        self.play(ShowCreation(frame))
        self.activate_zooming()
        #'''
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim
        )
        self.play(Write(texto1))
        #'''
        self.wait()
        '''
        self.play(
            #self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        #'''
        self.play(
            frame.shift,UP,
            )
        self.play(Write(texto2))
        self.wait()
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        self.play(
            zoomed_display.display_frame.fade,1,
            frame.fade,1
            )
        self.wait()


class VideoWrapper(Scene):
    def construct(self):
        fade_rect = FullScreenFadeRectangle()
        fade_rect.set_fill(DARK_GREY, 1)
        screen_rect = ScreenRectangle()
        screen_rect.set_height(4)
        screen_rect.set_fill(BLACK, 1)
        screen_rect.set_stroke(width=0)

        boundary = AnimatedBoundary(screen_rect)

        title = TextMobject("Learn the math")
        title.scale(1.5)
        title.next_to(screen_rect, UP)

        self.add(fade_rect)
        self.add(screen_rect)
        self.add(boundary)

        self.play(FadeInFromDown(title))
        self.wait(19)

class ReadQuestions(Scene):
    def construct(self):
        background = ImageMobject("img/celular_amazon.png")
        background.set_height(FRAME_HEIGHT)
        self.add(background)

        lines = SVGMobject("svg_images/cursor.svg")
        lines.set_width(FRAME_WIDTH - 1)
        lines.move_to(0.1 * DOWN)
        lines.set_stroke(TEAL, 3)

        clump_sizes = [1, 2, 3, 2, 1, 2]
        partial_sums = list(np.cumsum(clump_sizes))
        clumps = VGroup(*[
            lines[i:j]
            for i, j in zip(
                [0] + partial_sums,
                partial_sums,
            )
        ])

        faders = []
        for clump in clumps:
            rects = VGroup()
            for line in clump:
                rect = Rectangle()
                rect.set_stroke(width=0)
                rect.set_fill(TEAL, 0.25)
                rect.set_width(line.get_width() + SMALL_BUFF)
                rect.set_height(0.35, stretch=True)
                rect.move_to(line, DOWN)
                rects.add(rect)

            self.play(
                ShowCreation(clump, run_time=2),
                FadeIn(rects),
                *faders,
            )
            self.wait()
            faders = [
                FadeOut(clump),
                FadeOut(rects),
            ]
        self.play(*faders)
        self.wait()




class OpeningQuote(Scene):
    def construct(self):
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
        author = TextMobject("--Alan Turing")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(1)
        self.play(Write(author, run_time = 4))
        self.wait()


class NumericVsGeometric(Scene):
    def construct(self):
        self.setup()
        self.specifics_concepts()

    def setup(self):
        numeric = TextMobject("Numeric operations")
        geometric = TextMobject("Geometric intuition")
        for mob in numeric, geometric:
            mob.to_corner(UP+LEFT)
        geometric.shift(FRAME_X_RADIUS*RIGHT)
        hline = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        hline.next_to(numeric, DOWN)
        hline.to_edge(LEFT, buff = 0)
        vline = Line(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        for mob in hline, vline:
            mob.set_color(GREEN)

        vmobj = VMobject(hline, vline)
        self.play(Write(vmobj))
        digest_locals(self)

    def specifics_concepts(self):
        matrix_vector_product = TexMobject(" ".join([
            matrix_to_tex_string(EXAMPLE_TRANFORM),
            matrix_to_tex_string(TRANFORMED_VECTOR),
            "&=",
            matrix_to_tex_string([
                ["1 \\cdot 1 + 0 \\cdot 2"], 
                ["1 \\cdot 1 + (-1)\\cdot 2"]
            ]),
            "\\\\ &=",
            matrix_to_tex_string([[1], [-1]]),
        ]))
        matrix_vector_product.set_width(FRAME_X_RADIUS-0.5)
        matrix_vector_product.next_to(self.vline, LEFT)

        self.play(
            Write(self.numeric),
            FadeIn(matrix_vector_product),
            run_time = 2
        )
        self.wait()
        self.play(Write(self.geometric, run_time = 2))
        ### Paste in linear transformation
        self.wait()
        digest_locals(self)



class Texto(TextMobject):
    pass

class Formula(TexMobject):
    pass

class TextoB(TextMobject):
    CONFIG={
    "color": WHITE,
    }

class TextoN(TextMobject):
    CONFIG={
    "color": BLACK,
    }

class FormulaB(TexMobject):
    CONFIG={
    "color": WHITE,
    }  

class FormulaN(TexMobject):
    CONFIG={
    "color": BLACK,
    }  

class WriteOpeningWords(Scene):
    def construct(self):
        raw_string1 = "Dear calculus student,"
        raw_string2 = "You're about to go through your first course. Like " + \
                      "any new topic, it will take some hard work to understand,"
        words1, words2 = [
            TextMobject("\\Large ", *rs.split("  "))
            for rs in (raw_string1, raw_string2)
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStartMap(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)

class Justificado(Scene):
    def construct(self):
        texto=Texto("""
        \\justify
This  is  the  second  paragraph. Hello, here is some text without
a meaning.  This text should show what 
a printed text will look like at this place.  If you read this text, 
you will get no information.  Really?  Is there no information?  Is there 
a difference between this text and some nonsense like not at all!  A 
blind text like this gives you information about the selected font, how 
the letters are written and an impression of the look.  This text should
contain all letters of the alphabet and it should be written in of the
original language.There is no need for special content, but the length of
words should match the language.
        """).scale(0.7)
        self.play(LaggedStart(FadeIn(texto)))
        self.wait()


class WriteStuff3(Scene):
    def construct(self):
        example_tex = TexMobject(
            "{\\sf","print","(","`Hello, world!'",")}",
            tex_to_color_map={"print": YELLOW, "`Hello, world!'": ORANGE}
        )

        self.play(Write(example_tex))
        self.wait()


class FondoTexto(Scene):
    def construct(self):
        texto=TexMobject("Hola","mundo")
        fondo=Square().set_fill(GREEN,1)

        self.tex_to_color_map = {
            "Hola": RED,
        }

        texto.set_color_by_tex_to_color_map(
                self.tex_to_color_map
            )
        self.add(fondo,texto)
        self.wait(4)


class Pantalla(Scene):
    def construct(self):
        height = self.camera.get_pixel_height()
        width = self.camera.get_pixel_width()
        print("%s x %s"%(height,width))
        self.add(Square())


class Layer(Scene):
    def construct(self):
        capa0=Square(color=RED,fill_opacity=0.5).scale(1.5)
        capa1=Square(color=BLUE,fill_opacity=0.5).scale(1.3)
        capa2=Circle(radius=1.5,fill_opacity=0.5,color=ORANGE)
        self.add(capa0,capa1,capa2)
        self.wait(3)
        self.bring_to_front(capa1) 
        self.wait()
        self.bring_to_front(capa0)
        self.wait()
        self.bring_to_back(capa0)
        self.wait()


class PerTexto(Scene):
    def construct(self):
        texto=Texto("Q","u","é","\\_","o","n","d","a","\\_","g","e","n","t","e")
        for i in [3,8]:
            texto[i].fade(1)
        texto_base=Texto("Qué\\_onda\\_gente")
        for i in range(len(texto)):
            texto[i].move_to(texto_base[i])
        self.play(Escribe(texto))
        self.add(*[Perturbacion(texto[i])for i in range(len(texto))])
        self.wait(5)


class NewtonVsJohann(Scene):
    def construct(self):
        newton, johann = [
            ImageMobject(name, invert = False).scale(0.5)
            for name in ("Newton", "Johann_Bernoulli2")
        ]
        greater_than = TexMobject(">")
        newton.next_to(greater_than, RIGHT)
        johann.next_to(greater_than, LEFT)
        self.add(johann, greater_than, newton)
        for i in range(2):
            kwargs = {
                "path_func" : counterclockwise_path(),
                "run_time"  : 2 
            }
            self.play(
                ApplyMethod(newton.replace, johann, **kwargs),
                ApplyMethod(johann.replace, newton, **kwargs),
            )
            self.wait()

class MultipleDefinitionsOfAnEllipse(Scene):
    def construct(self):
        title = Title("Multiple definitions of ``ellipse''")
        self.add(title)

        definitions = VGroup(
            TextMobject("1. Stretch a circle"),
            TextMobject("2. Thumbtack \\\\ \\quad\\, construction"),
            TextMobject("3. Slice a cone"),
        )
        definitions.arrange(
            DOWN, buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        definitions.next_to(title, DOWN, LARGE_BUFF)
        definitions.to_edge(LEFT)

        for definition in definitions:
            definition.saved_state = definition.copy()
            definition.saved_state.set_fill(LIGHT_GREY, 0.5)

        self.play(LaggedStartMap(
            FadeInFrom, definitions,
            lambda m: (m, RIGHT),
            run_time=4
        ))
        self.wait()
        for definition in definitions:
            others = [d for d in definitions if d is not definition]
            self.play(
                definition.set_fill, WHITE, 1,
                definition.scale, 1.2, {"about_edge": LEFT},
                *list(map(Restore, others))
            )
            self.wait(2)


class Goals(Scene):
    def construct(self):
        goals = [
            TextMobject("Goal %d:"%d, s)
            for d, s in [
                (1, "Formal definition of derivatives"),
                (2, "$(\\epsilon, \\delta)$ definition of a limit"),
                (3, "L'Hôpital's rule"),
            ]
        ]
        for goal in goals:
            goal.scale(1.3)
            goal.shift(3*DOWN).to_edge(LEFT)

        curr_goal = goals[0]
        self.play(FadeIn(curr_goal))
        self.wait(2)
        for goal in goals[1:]:
            self.play(Transform(curr_goal, goal))
            self.wait(2)


def Celular():
    pad = SVGMobject(
        file_name = "svg_images/mobile.svg",
        fill_opacity = 1,
        stroke_width = 1,
        height = 8,
        stroke_color = WHITE,
    )
    pad[0].set_fill(WHITE)
    pad[1].set_fill(BLACK)
    pad[2].set_fill(None,0)
    pad[2].set_stroke(WHITE,0.5)
    pad[3].set_fill(BLACK)
    pad[4].set_fill(BLACK)
    pad[5].set_fill(BLACK)
    return pad

class Pad(Scene):
    CONFIG={"camera_config":{"background_color":'#23262b'}}
    def construct(self):
        pad = Celular()

        self.play(DrawBorderThenFill(pad))
        self.play(pad.rotate,np.pi/2,
            pad.scale,1.6,
            pad.shift,UP*0.7
            )
        propietario="Propietario del video"
        subtexto=TextMobject("Propietario:",propietario).to_edge(DL).shift(DOWN*0.3)
        texto=TextMobject("Video: Titulo del video").next_to(subtexto,UP).align_to(subtexto,LEFT)
        #leyenda=VGroup(texto,subtexto).arrange_submobjects(LEFT)
        self.play(Write(texto),Write(subtexto))
        self.wait()



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



# 3b1b ---- animations

class PhaseSpaceTitle(Scene):
    def construct(self):
        title = TextMobject("Phase space")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)
        self.add(rect)
        self.play(Write(title, run_time=1))
        self.wait()


class FromPuzzleToSolution(MovingCameraScene):
    def construct(self):
        big_rect = FullScreenFadeRectangle()
        big_rect.set_fill(DARK_GREY, 0.5)
        self.add(big_rect)

        rects = VGroup(ScreenRectangle(), ScreenRectangle())
        rects.set_height(3)
        rects.arrange(RIGHT, buff=2)

        titles = VGroup(
            TextMobject("Puzzle"),
            TextMobject("Solution"),
        )

        images = Group(
            ImageMobject("BlocksAndWallExampleMass16"),
            ImageMobject("AnalyzeCircleGeometry"),
        )
        for title, rect, image in zip(titles, rects, images):
            title.scale(1.5)
            title.next_to(rect, UP)
            image.replace(rect)
            self.add(image, rect, title)

        frame = self.camera_frame
        frame.save_state()

        self.play(
            frame.replace, images[0],
            run_time=3
        )
        self.wait()
        self.play(Restore(frame, run_time=3))
        self.play(
            frame.replace, images[1],
            run_time=3,
        )
        self.wait()


class HangingWeightsScene(MovingCameraScene):
    CONFIG = {
        "frequency" : 0.5,
        "ceiling_radius" : 3*FRAME_X_RADIUS,
        "n_springs" : 72,
        "amplitude" : 0.6,
        "spring_radius" : 0.15,
    }
    def construct(self):
        self.setup_springs()
        self.setup_weights()
        self.introduce()
        self.show_analogy_with_electron()
        self.metaphor_for_something()
        self.moving_reference_frame()

    def setup_springs(self):
        ceiling = self.ceiling = Line(LEFT, RIGHT)
        ceiling.scale(self.ceiling_radius)
        ceiling.to_edge(UP, buff = LARGE_BUFF)
        self.add(ceiling)

        def get_spring(alpha, height = 2):
            t_max = 6.5
            r = self.spring_radius
            s = (height - r)/(t_max**2)
            spring = ParametricFunction(
                lambda t : op.add(
                    r*(np.sin(TAU*t)*RIGHT+np.cos(TAU*t)*UP),
                    s*((t_max - t)**2)*DOWN,
                ),
                t_min = 0, t_max = t_max,
                color = WHITE,
                stroke_width = 2,
            )
            spring.alpha = alpha
            spring.move_to(ceiling.point_from_proportion(alpha), UP)
            spring.color_using_background_image("grey_gradient")
            return spring
        alphas = np.linspace(0, 1, self.n_springs)
        bezier([0, 1, 0, 1])
        springs = self.springs = VGroup(*list(map(get_spring, alphas)))

        k_tracker = self.k_tracker = VectorizedPoint()
        t_tracker = self.t_tracker = VectorizedPoint()
        always_shift(t_tracker, RIGHT, 1)
        self.t_tracker_walk = t_tracker
        equilibrium_height = springs.get_height()
        def update_springs(springs):
            for spring in springs:
                k = k_tracker.get_center()[0]
                t = t_tracker.get_center()[0]
                f = self.frequency
                x = spring.get_top()[0]
                A = self.amplitude
                d_height = A*np.cos(TAU*f*t - k*x)
                new_spring = get_spring(spring.alpha, 2+d_height)
                Transform(spring, new_spring).update(1)
        spring_update_anim = Mobject.add_updater(springs, update_springs)
        self.spring_update_anim = spring_update_anim
        spring_update_anim.update(0)

        self.play(
            ShowCreation(ceiling),
            LaggedStartMap(ShowCreation, springs)
        )

    def setup_weights(self):
        weights = self.weights = VGroup()
        weight_anims = weight_anims = []
        for spring in self.springs:
            x = spring.get_top()[0]
            mass = np.exp(-0.1*x**2)
            weight = Circle(radius = 0.15)
            weight.start_radius = 0.15
            weight.target_radius = 0.25*mass #For future update
            weight.spring = spring
            weight_anim = Mobject.add_updater(
                weight, lambda w : w.move_to(w.spring.get_bottom())
            )
            weight_anim.update(0)
            weight_anims.append(weight_anim)
            weights.add(weight)
        weights.set_fill(opacity = 1)
        weights.set_color_by_gradient(BLUE_D, BLUE_E, BLUE_D)
        weights.set_stroke(WHITE, 1)

        self.play(LaggedStartMap(GrowFromCenter, weights))
        self.add(self.t_tracker_walk)
        self.add(self.spring_update_anim)
        self.add(*weight_anims)

    def introduce(self):
        arrow = Arrow(4*LEFT, LEFT)
        arrows = VGroup(arrow, arrow.copy().flip(about_point = ORIGIN))
        arrows.set_color(WHITE)

        self.wait(3)
        self.play(*list(map(GrowArrow, arrows)))
        self.play(*[
            UpdateFromAlphaFunc(
                weight, lambda w, a : w.set_width(
                    2*interpolate(w.start_radius, w.target_radius, a)
                ),
                run_time = 2
            )
            for weight in self.weights
        ])
        self.play(FadeOut(arrows))
        self.wait(3)

    def show_analogy_with_electron(self):
        words = TextMobject(
            "Analogous to the energy of a particle \\\\",
            "(in the sense of $E=mc^2$)"
        )
        words.move_to(DOWN)

        self.play(Write(words))
        self.wait(3)
        self.play(FadeOut(words))

    def metaphor_for_something(self):
        de_broglie = ImageMobject("de_Broglie")
        de_broglie.set_height(3.5)
        de_broglie.to_corner(DOWN+RIGHT)
        words = TextMobject("""
            If a photon's energy is carried as a wave \\\\
            is this true for any particle?
        """)
        words.next_to(de_broglie, LEFT)

        einstein = ImageMobject("Einstein")
        einstein.match_height(de_broglie)
        einstein.to_corner(DOWN+LEFT)

        for picture in de_broglie, einstein:
            picture.backdrop = Rectangle()
            picture.backdrop.replace(picture, stretch = True)
            picture.backdrop.set_fill(BLACK, 1)
            picture.backdrop.set_stroke(BLACK, 0)

        self.play(
            Animation(de_broglie.backdrop, remover = True),
            FadeIn(de_broglie)
        )
        self.play(Write(words))
        self.wait(7)
        self.play(
            FadeOut(words),
            Animation(einstein.backdrop, remover = True),
            FadeIn(einstein)
        )
        self.wait(2)

        self.de_broglie = de_broglie
        self.einstein = einstein

    def moving_reference_frame(self):
        rect = ScreenRectangle(height = 2.1*FRAME_Y_RADIUS)
        rect_movement = always_shift(rect, direction = LEFT, rate = 2)
        camera_frame = self.camera_frame

        self.add(rect)
        self.play( 
            Animation(self.de_broglie.backdrop, remover = True),
            FadeOut(self.de_broglie),
            Animation(self.einstein.backdrop, remover = True),
            FadeOut(self.einstein),
        )
        self.play(camera_frame.scale, 3, {"about_point" : 2*UP})
        self.play(rect.shift, FRAME_WIDTH*RIGHT, path_arc = -TAU/2)
        self.add(rect_movement)
        self.wait(3)

        def zoom_into_reference_frame():
            original_height = camera_frame.get_height()
            original_center = camera_frame.get_center()
            self.play(
                UpdateFromAlphaFunc(
                    camera_frame, lambda c, a : c.set_height(
                        interpolate(original_height, 0.95*rect.get_height(), a)
                    ).move_to(
                        interpolate(original_center, rect.get_center(), a)
                    )
                ),
                ApplyMethod(self.k_tracker.shift, RIGHT)
            )
            self.play(MaintainPositionRelativeTo(
                camera_frame, rect,
                run_time = 6
            ))
            self.play(
                camera_frame.set_height, original_height,
                camera_frame.move_to, original_center,
                ApplyMethod(self.k_tracker.shift, LEFT)
            )

        zoom_into_reference_frame()
        self.wait()
        self.play(
            UpdateFromAlphaFunc(rect, lambda m, a : m.set_stroke(width = 2*(1-a)))
        )

        index = int(0.5*len(self.springs))
        weights = VGroup(self.weights[index], self.weights[index+4])
        flashes = list(map(self.get_peak_flash_anim, weights))
        weights.save_state()
        weights.set_fill(RED)
        self.add(*flashes)
        self.wait(5)

        rect.align_to(camera_frame, RIGHT)
        self.play(UpdateFromAlphaFunc(rect, lambda m, a : m.set_stroke(width = 2*a)))

        randy = Randolph(mode = "pondering")
        randy.look(UP+RIGHT)
        de_broglie = ImageMobject("de_Broglie")
        de_broglie.set_height(6)
        de_broglie.next_to(4*DOWN, DOWN)
        self.add(
            Mobject.add_updater(
                randy, lambda m : m.next_to(
                    rect.get_corner(DOWN+LEFT), UP+RIGHT, MED_LARGE_BUFF,
                ).look_at(weights)
            ),
            de_broglie
        )
        self.wait(2)

        zoom_into_reference_frame()
        self.wait(8)

    ###

    def get_peak_flash_anim(self, weight):
        mobject = Mobject() #Dummy
        mobject.last_y = 0
        mobject.last_dy = 0
        mobject.curr_anim = None
        mobject.curr_anim_time = 0
        mobject.time_since_last_flash = 0
        def update(mob, dt):
            mob.time_since_last_flash += dt
            point = weight.get_center()
            y = point[1]
            mob.dy = y - mob.last_y
            different_dy = np.sign(mob.dy) != np.sign(mob.last_dy)
            if different_dy and mob.time_since_last_flash > 0.5:
                mob.curr_anim = Flash(
                    VectorizedPoint(point),
                    flash_radius = 0.5,
                    line_length = 0.3,
                    run_time = 0.2,
                )
                mob.submobjects = [mob.curr_anim.mobject]
                mob.time_since_last_flash = 0
            mob.last_y = float(y)
            mob.last_dy = float(mob.dy)
            ##
            if mob.curr_anim:
                mob.curr_anim_time += dt
                if mob.curr_anim_time > mob.curr_anim.run_time:
                    mob.curr_anim = None
                    mob.submobjects = []
                    mob.curr_anim_time = 0
                    return
                mob.curr_anim.update(mob.curr_anim_time/mob.curr_anim.run_time)

        return Mobject.add_updater(mobject, update)

class MinutPhysicsWrapper(Scene):
    def construct(self):
        logo = ImageMobject("minute_physics_logo", invert = True)
        logo.to_corner(UP+LEFT)
        self.add(logo)

        title = TextMobject("Minute Physics on special relativity")
        title.to_edge(UP).shift(MED_LARGE_BUFF*RIGHT)

        screen_rect = ScreenRectangle()
        screen_rect.set_width(title.get_width() + LARGE_BUFF)
        screen_rect.next_to(title, DOWN)

        self.play(ShowCreation(screen_rect))
        self.play(Write(title))
        self.wait(2)


"""
============================================
=========      NETWORK SCENES     ==========
============================================
"""

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


class LayOutPlan(NetworkScene):
    CONFIG = {
        # "layer_sizes" : DEFAULT_LAYER_SIZES,
        "network_mob_config" : {
            "neuron_to_neuron_buff" : MED_LARGE_BUFF,
            "layer_to_layer_buff" : 1,
            "edge_stroke_width" : 1.2,
            # "neuron_stroke_color" : GOLD,
            # "neuron_stroke_width" : 2,
            # "neuron_fill_color" : WHITE,
            # "average_shown_activation_of_large_layer" : False,
            "edge_propogation_color" : YELLOW_E,
            "edge_propogation_time" : 2,
            # "include_output_labels" : True,
        },
        # "n_examples" : 15,
        # "max_stroke_width" : 3,
        # "stroke_width_exp" : 3,
        # "eta" : 3.0,
        "positive_edge_color" : GREEN,
        "negative_edge_color" : RED,
        "positive_change_color" : BLUE_C,
        "negative_change_color" : average_color(*2*[RED] + [YELLOW]),
        "default_activate_run_time" : 1.2,
    }
    def setup(self):
        # TeacherStudentsScene.setup(self)
        NetworkScene.setup(self)
        self.remove(self.network_mob)

    def construct(self):
        # self.force_skipping()

        self.show_words()
        self.show_network()
        self.show_input_document()
        self.show_output_layer()
        # self.show_math()
        # self.ask_about_layers()
        self.show_learning()
        #self.show_videos()

    def show_words(self):
        words = VGroup(
            TextMobject("Aprendizaje", " automatico").set_color(GREEN),
            TextMobject("Red Neuronal").set_color(BLUE),
        )
        words[0].save_state()
        words[0].shift(DOWN)
        words[0].fade(1)

        self.play(words[0].restore)
        self.play(
            words[0].shift, MED_LARGE_BUFF*UP,
            FadeIn(words[1]),
        )
        self.play(words.to_corner, UP+RIGHT)
        self.words = words

    def show_network(self):
        network_mob = self.network_mob
        self.play(
            ReplacementTransform(
                VGroup(self.words[1].copy()),
                network_mob.layers
            ),
            run_time = 1
        )
        self.play(ShowCreation(
            network_mob.edge_groups,
            lag_ratio = 0.5,
            run_time = 2,
            rate_func=linear,
        ))

        self.wait()
        # in_vect = np.random.random(self.network.sizes[0])
        # self.feed_forward(in_vect)

    def show_math(self):
        equation = TexMobject(
            "\\textbf{a}_{l+1}", "=",  
            "\\sigma(",
                "W_l", "\\textbf{a}_l", "+", "b_l",
            ")"
        )
        equation.set_color_by_tex_to_color_map({
            "\\textbf{a}" : GREEN,
        })
        equation.move_to(self.network_mob.get_corner(UP+RIGHT))
        equation.to_edge(UP)

        #self.play(Write(equation, run_time = 2))
        #self.wait()
        self.equation = equation

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
        self.learning_word = word

    def show_input_document(self):
        document = self.get_document()
        document.to_edge(LEFT)
        #document.scale(0.7)
        document.shift(0.5*UP + RIGHT)
        document_copy = document.copy()

        network_mob = self.network_mob
        layers = network_mob.layers
        layers.save_state()

        input_layer = layers[0]
        all_edges = VGroup(*it.chain(*network_mob.edge_groups))
        
        self.play(ShowCreation(document), ShowCreation(document_copy))

        edge_animation = LaggedStartMap(
            ShowCreationThenDestruction, 
            all_edges.copy().set_fill(YELLOW).set_color(YELLOW).set_stroke(width=1.8),
            run_time = 4,
            lag_ratio = 0.1,
            remover = True,
        )
        
        layer_animation = Transform(
            # VGroup(*layers), VGroup(*active_layers),
            document_copy, input_layer,
            run_time = 1,
            # lag_ratio = 0.5,
            rate_func=linear,
        )
        self.play(layer_animation)
        self.play(edge_animation)

        self.document = document
        

    
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
        document = VGroup(rect, lines, text)
        # signature = get_cursive_name("Texto")
        # signature.set_color(self.signature_color)
        # line = document[1][-1]
        # signature.next_to(line, UP, SMALL_BUFF)
        return document

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
        self.play(
            neuron.restore,
            neuron.set_fill, None, 1,
            label.restore,
            FadeOut(activation),
        )
        self.wait()

        self.labels = labels

    def show_videos(self):
        network_mob = self.network_mob
        learning = self.learning_word
        structure = TextMobject("Structure")
        structure.set_color(YELLOW)
        videos = VGroup(*[
            VideoIcon().set_fill(RED)
            for x in range(2)
        ])
        videos.set_height(1.5)
        videos.arrange(RIGHT, buff = LARGE_BUFF)
        videos.next_to(self.students, UP, LARGE_BUFF)

        network_mob.generate_target()
        network_mob.target.set_height(0.8*videos[0].get_height())
        network_mob.target.move_to(videos[0])
        learning.generate_target()
        learning.target.next_to(videos[1], UP)
        structure.next_to(videos[0], UP)
        structure.shift(0.5*SMALL_BUFF*UP)

        self.revert_to_original_skipping_status()
        self.play(
            MoveToTarget(network_mob),
            MoveToTarget(learning)
        )
        self.play(
            DrawBorderThenFill(videos[0]),
            FadeIn(structure),
            self.get_student_changes(*["pondering"]*3)
        )
        self.wait()
        self.play(DrawBorderThenFill(videos[1]))
        self.wait()