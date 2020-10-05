#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
import sys
import inspect
from PIL import Image
import cv2
import random
from scipy.spatial.distance import cdist
from scipy import ndimage

from manimlib.imports import *


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
    def __init__(self,texto,buff=0.07,**kwargs):
        Line.__init__(self,texto.get_corner(DL),texto.get_corner(DR),**kwargs)
        self.shift(DOWN*buff)


class MainPresentation(MovingCameraScene):
    def construct(self):
        # self.show_quote()
        # self.remove_all_obj_in_scene()
        # self.show_title()
        # self.introduction()
        # self.show_amazon_example()
        # self.remove_all_obj_in_scene()
        self.show_opinions_example()

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
                run_time=3)
            self.wait(5)
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
            question_1 = TextMobject('¿Que entendemos por "Opinion"?')
            self.play(Write(question_1))
            self.wait()
            text1 = TextMobject("This is a bouncing ball")
            text2 = TextMobject("Enjoy watching!")
            self.wait(1)
            self.play(FadeOut(question_1), FadeIn(text1))

            self.wait(2)
            self.play(Transform(text1, text2))

            self.wait(10)


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

        sentiment_rect = Rectangle(height=2.2, width=2.7)
        sentiment_rect.set_color(YELLOW_E)
        sentiment_rect.move_to(2.7*UP + 5.3*LEFT)

        absa_rect = Rectangle(height=2.3, width=3)
        absa_rect.set_color(GREEN)
        absa_rect.move_to(5.15*LEFT)

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
        
        self.play(Restore(saved_frame))

        frame = saved_frame
        frame.generate_target()
        frame.target.scale(0.72)
        frame.target.move_to(rects[3])

        self.play(
            ShowCreation(rects[1]),
            ShowCreation(rects[2]),
            MoveToTarget(frame, run_time=3),
            Transform(big_rect, big_rects[3]),
        )

        self.wait()

        self.play(FadeOut(big_rect), Restore(saved_frame))
        
        self.wait()



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


class ZoomT2(ZoomedScene):
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
