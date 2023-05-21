import cv2
import os
import random
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from urllib.request import urlopen
from deepface import DeepFace
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen

fontName='SUITE-Variable.ttf'


def draw_face_border(img, pt1, pt2, color, thickness, r, d):
    x1, y1 = pt1
    x2, y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


class KivyCamera(Image):
    # Global to call on click events easily
    play = 0
    stop = 0
    sound = ""
    textout = ""
    isPlaying = False
    frame = ""
    menu_images = ['food1.jpg', 'food2.jpg', 'food3.jpg', 'food4.jpg']
    rank = {}

    def __init__(self, capture, fps, layout, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)
        self.index = 0
        self.menu_images = ['food1.jpg', 'food2.jpg', 'food3.jpg', 'food4.jpg', 'food5.jpg',
                            'food6.jpg', 'food7.jpg', 'food8.jpg', 'food9.jpg', 'food10.jpg']
        random.shuffle(self.menu_images)
        self.image = Image(source=self.menu_images[self.index])
        width = 800
        height = 960
        self.image.size = (width, height)
        self.add_widget(self.image)

        # Button
        self.play = Button(text="다음", font_name=fontName, size_hint=(.1, .1))
        self.stop = Button(text="결과 보기", font_name=fontName, size_hint=(.1, .1))
        self.stop.bind(on_release=self.triggerStop)
        layout.add_widget(self.play)
        layout.add_widget(self.stop)



    def update(self, bt=None):
        ret, frame = self.capture.read()
        if ret:
            face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.3, 4)
            for (x, y, w, h) in faces:
                # To draw a rectangle in a face
                draw_face_border(frame, (x, y), (x + w, y + h), (132, 0, 255), 2, 15, 10)
            cv2.putText(frame, self.textout.capitalize(), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 145, 255), 2)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.texture = image_texture
        self.play.fbind('on_press', self.triggerPlay, frame)


    def change_image(self, dt):
        self.index = (self.index + 1) % len(self.menu_images)
        self.image.source = self.menu_images[self.index]

    def triggerPlay(self, frame, bt=None):
        try:
            listobj = DeepFace.analyze(frame, actions=['emotion'])
            emotion = listobj['emotion']["happy"]
            self.rank[f"{self.menu_images[self.index]}"] = {"emotion": 'happy', "emotion_prob": emotion}
            print(self.rank)
            self.textout = "happy: " + str(emotion)

            if self.isPlaying:
                self.sound.stop()

            Clock.schedule_once(self.change_image, 1/30)

            if self.sound:
                self.sound.play()
                self.isPlaying = True

        except ValueError:
            self.textout = "Face Not Found..."

        except FileNotFoundError:
            self.textout = "Food File Does Not Exist..."

        return exit

    def triggerStop(self, instance):

        ranked = sorted(self.rank.items(), key=lambda x: x[1]["emotion_prob"] if x[1]["emotion"] == "happy" else 0,
                        reverse=True)
        texts =["음식 추천 결과"]


        for i, (index, value) in enumerate(ranked):
            if index == 'food1.jpg':
                index = '짜장면'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food2.jpg':
                index = '삼겹살'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food3.jpg':
                index = '치킨'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food4.jpg':
                index = '피자'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food5.jpg':
                index = '돈까스'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food6.jpg':
                index = '족발'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food7.jpg':
                index = '초밥'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food8.jpg':
                index = '김치찌개'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food9.jpg':
                index = '보쌈'
                texts.append(f"{i + 1}위 - {index}")
            if index == 'food10.jpg':
                index = '파스타'
                texts.append(f"{i + 1}위 - {index}")


        content = NewWindowContent(texts=texts)
        popup = Popup(title='Food Rank', content=content, size_hint=(None, None), size=(600, 400))
        popup.open()

class NewWindowContent(BoxLayout):
    def __init__(self, texts, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        for text in texts:
            self.add_widget(Label(text=text, font_name=fontName, font_size=15))

class MFTI(App):
    def build(self):
        # Icon
        self.icon = 'assets/logo.png'

        # Layout
        floatLayout = FloatLayout()
        horizontalLayout = BoxLayout(orientation='horizontal')
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=60, layout=horizontalLayout,
                                    size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.35})


        # Set the desired size and position for the camera window
        self.my_camera.width = 500
        self.my_camera.height = 300
        self.my_camera.x = (floatLayout.width - self.my_camera.width) / 2
        self.my_camera.y = (floatLayout.height - self.my_camera.height) / 8

        # Add Layouts
        floatLayout.add_widget(horizontalLayout)
        floatLayout.add_widget(self.my_camera)
        return floatLayout

    def on_stop(self):
        # without this, app will not exit even if the window is closed
        KivyCamera.triggerStop(self.my_camera)
        self.capture.release()


if __name__ == '__main__':
    MFTI().run()