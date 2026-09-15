# AirCanvas (Virtual Paint) 🎨🖐️

The **AirCanvas** project allows you to draw on your computer screen in real-time using hand gestures in front of a webcam. The application uses computer vision to track finger movements and overlay the drawing onto the video stream.

---

## 📁 Project Structure

```text
AirCanva/
├── main.py                # Main application script (video capture, tracking, drawing)
├── requirements.txt       # List of external Python dependencies
├── hand_landmarker.task   # MediaPipe model for hand landmark recognition
├── .gitignore             # Git version control exclusions
└── README.md              # Project documentation

```

### File Purposes:

* **`main.py`** — contains the main processing loop: capturing frames from the webcam, recognizing hands using `cvzone`, handling finger gestures, drawing lines on a graphical canvas, and merging the canvas with the live video stream.
* **`requirements.txt`** — required libraries (OpenCV, cvzone, MediaPipe, NumPy, etc.).
* **`hand_landmarker.task`** — pre-trained MediaPipe Tasks API model for detecting and localizing 21 hand landmarks.

---

## 📦 Dependencies and Their Roles

Main libraries used in the project:

1. **`opencv-python` / `opencv-contrib-python` (`cv2`)**:
* Video stream capture from the webcam (`cv2.VideoCapture`).
* Frame processing (mirroring `cv2.flip`, layer blending, color space conversions).
* Drawing graphical primitives (circles `cv2.circle`, lines `cv2.line`, text `cv2.putText`).
* Displaying the final window (`cv2.imshow`).


2. **`cvzone` (`HandTrackingModule.HandDetector`)**:
* Convenient high-level wrapper over MediaPipe.
* Detects hands in a frame (`findHands`) and determines finger states: raised/lowered (`fingersUp`).


3. **`mediapipe`**:
* Google's framework for real-time computer vision ML models. Powers hand detection in `cvzone`.


4. **`numpy`**:
* Pixel matrix manipulations.
* Initializing a clean canvas (`np.zeros_like(frame)`) where drawing takes place.



---

## 🔍 Detailed Code Walkthrough (`main.py`)

Let's break down the program's logic step by step:

### 1. Camera and Detector Initialization

```python
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # Frame width
cap.set(4, 720)  # Frame height

detector = HandDetector(detectionCon=0.8, maxHands=1)

```

* Connects to the first available webcam (`0`) and sets the resolution to `1280x720`.
* Creates a `HandDetector` object with an 80% recognition confidence threshold (`detectionCon=0.8`) and a limit of 1 hand per frame.

### 2. Canvas Variables Setup

```python
canvas = None
xp, yp = 0, 0          # Previous coordinates of the fingertip
brush_thickness = 15   # Brush thickness
eraser_thickness = 50  # Eraser thickness
draw_color = (0, 255, 0) # Drawing color BGR (green)

```

### 3. Main Frame Processing Loop

```python
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1) # Mirror the frame for convenience
    if canvas is None:
        canvas = np.zeros_like(frame) # Create a blank black canvas matching frame size

```

### 4. Gesture Recognition and Actions Logic

Using `detector.findHands`, we get a list of detected hands and landmarks (`lmList`).

* **Landmark 8** — tip of the index finger (`x1, y1`).
* **Landmark 12** — tip of the middle finger (`x2, y2`).
* `fingers = detector.fingersUp(hand)` returns an array of 5 elements `[thumb, index, middle, ring, pinky]` (`1` - raised, `0` - lowered).

#### 🛠️ Eraser Mode

```python
if fingers[1] and fingers[2]:
    cv2.circle(frame, (x1, y1), eraser_thickness // 2, (0, 0, 255), -1)
    if xp == 0 and yp == 0:
        xp, yp = x1, y1
    cv2.line(canvas, (xp, yp), (x1, y1), (0, 0, 0), eraser_thickness)
    xp, yp = x1, y1

```

* **Gesture**: **index** and **middle** fingers are raised.
* A red eraser pointer circle is drawn on the frame.
* A black line `(0, 0, 0)` of `eraser_thickness` is drawn on the `canvas`, "erasing" what was drawn.

#### 🖌️ Drawing Mode

```python
elif fingers[1] and not fingers[2]:
    cv2.circle(frame, (x1, y1), brush_thickness // 2, draw_color, -1)
    if xp == 0 and yp == 0:
        xp, yp = x1, y1
    cv2.line(canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
    xp, yp = x1, y1

```

* **Gesture**: only the **index** finger is raised (middle finger is lowered).
* Draws a line of the selected `draw_color` from the previous point `(xp, yp)` to the current point `(x1, y1)`.

#### 🧹 Canvas Clear

```python
elif all(fingers[1:]):
    canvas = np.zeros_like(frame)
    cv2.putText(frame, "Canvas Cleared", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    xp, yp = 0, 0

```

* **Gesture**: all **4 fingers** are raised (index, middle, ring, pinky).
* The canvas is completely cleared (filled with zeros).

### 5. Combining Webcam Frame and Canvas

```python
img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
_, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
frame = cv2.bitwise_and(frame, img_inv)
frame = cv2.bitwise_or(frame, canvas)

```

1. Convert `canvas` to grayscale.
2. Create an inverted binary mask `img_inv`: where there is a drawing on the canvas, the mask becomes black (`0`).
3. Use `bitwise_and` to "cut out" the area for the drawing on the original webcam frame.
4. Use `bitwise_or` to overlay the colored pixels of the `canvas` onto the prepared frame.

---

## 🛠️ How to Modify and Customize Code

* **Change Brush Color**:
In `main.py`, modify the `draw_color` tuple in **BGR** format (Blue, Green, Red):
```python
draw_color = (255, 0, 0)   # Blue
draw_color = (0, 0, 255)   # Red
draw_color = (0, 255, 255) # Yellow

```


* **Change Brush or Eraser Thickness**:
```python
brush_thickness = 20   # Make brush thicker
eraser_thickness = 80  # Make eraser larger

```


* **Change Webcam Resolution**:
```python
cap.set(3, 1920) # Width
cap.set(4, 1080) # Height

```


* **Keybindings**:
The application exits when pressing the **`q`** key. To change the key, replace `'q'` with another letter:
```python
if cv2.waitKey(1) & 0xFF == ord('q'):
    break

```



---

## 🚀 Potential Improvements (Ideas for Future Development)

1. 🎨 **Interactive On-Screen Color Palette**:
* Draw colored rectangles at the top of the screen (red, green, blue, eraser).
* Automatically switch `draw_color` when hovering the index + middle finger over a rectangle area.


2. 📈 **Line Smoothing (Moving Average / Bezier)**:
* Smooth out fast hand movements using exponential smoothing or a Kalman filter for coordinates `(x1, y1)` to make drawing smoother.


3. ↩️ **Undo / Redo Stack**:
* Store canvas states in a `deque` history list to implement undoing the last stroke via a gesture or hotkey (e.g., `Ctrl+Z`).


4. 💾 **Save Drawing**:
* Add the ability to save the current canvas to a file (`.png` / `.jpg`) using a keypress (e.g., `s`) with `cv2.imwrite('drawing.png', canvas)`.


5. 🎛️ **Dynamic Brush Sizing by Gesture**:
* Read the distance between the thumb and index finger to dynamically change brush thickness right while drawing.


6. 🏗️ **OOP Code Structure**:
* Extract tracking, gesture processing, and canvas management logic into separate classes (`HandTracker`, `CanvasManager`, `UIOverlay`).
<div></b></div>

 # AirCanvas (Virtual Paint) 🎨🖐️


Проект **AirCanvas** позволяет рисовать на экране компьютера в режиме реального времени с помощью жестов рук перед веб-камерой. Приложение использует компьютерное зрение для отслеживания движения пальцев и наложения рисунка на видеопоток.


---


## 📁 Структура проекта


```text

AirCanva/

├── main.py # Основной скрипт приложения (захват видео, трекинг, рисование)

├── requirements.txt # Список внешних зависимостей Python

├── hand_landmarker.task # Модель MediaPipe для распознавания ключевых точек руки

├── .gitignore # Исключения для системы контроля версий Git

└── README.md # Документация проекта

```


### Назначение файлов:

* **`main.py`** — содержит весь основной цикл обработки: захват кадров с веб-камеры, распознавание рук с помощью `cvzone`, обработку жестов пальцев, отрисовку линий на графическом холсте и слияние холста с реальным видеопотоком.

* **`requirements.txt`** — библиотеки, необходимые для работы (OpenCV, cvzone, MediaPipe, NumPy и др.).

* **`hand_landmarker.task`** — предобученная модель MediaPipe Tasks API для детекции и локализации 21 ключевой точки на кисти руки.


---


## 📦 Зависимости и их роль


Основные библиотеки, используемые в проекте:


1. **`opencv-python` / `opencv-contrib-python` (`cv2`)**:

* Захват видеопотока с веб-камеры (`cv2.VideoCapture`).

* Обработка кадра (зеркальное отражение `cv2.flip`, смешивание слоев, цветовые преобразования).

* Отрисовка графических примитивов (круги `cv2.circle`, линии `cv2.line`, текст `cv2.putText`).

* Отображение итогового окна (`cv2.imshow`).


2. **`cvzone` (`HandTrackingModule.HandDetector`)**:

* Удобная высокоуровневая обертка над MediaPipe.

* Находит кисть руки на кадре (`findHands`) и определяет статус пальцев: поднят/опущен (`fingersUp`).


3. **`mediapipe`**:

* Фреймворк от Google для работы с ML-моделями компьютерного зрения в реальном времени. На его основе работает детекция рук в `cvzone`.


4. **`numpy`**:

* Манипуляции с матрицами пикселей.

* Инициализация чистого холста (`np.zeros_like(frame)`), на котором происходит рисование.


---


## 🔍 Подробный разбор кода (`main.py`)


Рассмотрим логику работы программы по шагам:


### 1. Инициализация камеры и детектора

```python

cap = cv2.VideoCapture(0)

cap.set(3, 1280) # Ширина кадра

cap.set(4, 720) # Высота кадра


detector = HandDetector(detectionCon=0.8, maxHands=1)

```

* Подключается первая доступная веб-камера (`0`) и задается разрешение `1280x720`.

* Создается объект `HandDetector` с порогом уверенности распознавания 80% (`detectionCon=0.8`) и ограничением в 1 руку на кадр.


### 2. Подготовка переменных холста

```python

canvas = None

xp, yp = 0, 0 # Предыдущие координаты кончика пальца

brush_thickness = 15 # Толщина кисти

eraser_thickness = 50 # Толщина ластика

draw_color = (0, 255, 0) # Цвет рисования BGR (зеленый)

```


### 3. Главный цикл обработки кадров

```python

while cap.isOpened():

success, frame = cap.read()

if not success:

break


frame = cv2.flip(frame, 1) # Зеркальный разворот кадра для удобства

if canvas is None:

canvas = np.zeros_like(frame) # Создаем пустой черный холст под размер кадра

```


### 4. Определение жестов и логика действий

С помощью `detector.findHands` получаем список найденных рук и ключевых точек (`lmList`).

* **Точка 8** — кончик указательного пальца (`x1, y1`).

* **Точка 12** — кончик среднего пальца (`x2, y2`).

* `fingers = detector.fingersUp(hand)` возвращает массив из 5 элементов `[большой, указательный, средний, безымянный, мизинец]` (`1` - поднят, `0` - опущен).


#### 🛠️ Режим ластика (Стирание)

```python

if fingers[1] and fingers[2]:

cv2.circle(frame, (x1, y1), eraser_thickness // 2, (0, 0, 255), -1)

if xp == 0 and yp == 0:

xp, yp = x1, y1

cv2.line(canvas, (xp, yp), (x1, y1), (0, 0, 0), eraser_thickness)

xp, yp = x1, y1

```

* **Жест**: поднят **указательный** и **средний** пальцы.

* На кадре рисуется красный круг-указатель ластика.

* На холсте `canvas` проводится черная линия `(0, 0, 0)` толщиной `eraser_thickness`, которая "стирает" нарисованное.


#### 🖌️ Режим рисования

```python

elif fingers[1] and not fingers[2]:

cv2.circle(frame, (x1, y1), brush_thickness // 2, draw_color, -1)

if xp == 0 and yp == 0:

xp, yp = x1, y1

cv2.line(canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)

xp, yp = x1, y1

```

* **Жест**: поднят **только указательный** палец (средний опущен).

* Проводится линия выбранного цвета `draw_color` от предыдущей точки `(xp, yp)` до текущей `(x1, y1)`.


#### 🧹 Очистка всего холста

```python

elif all(fingers[1:]):

canvas = np.zeros_like(frame)

cv2.putText(frame, "Canvas Cleared", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

xp, yp = 0, 0

```

* **Жест**: подняты **все 4 пальца** (указательный, средний, безымянный, мизинец).

* Холст полностью очищается (заполняется нулями).


### 5. Объединение кадра с веб-камеры и холста

```python

img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)

_, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)

img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)

frame = cv2.bitwise_and(frame, img_inv)

frame = cv2.bitwise_or(frame, canvas)

```

1. Переводим `canvas` в градации серого.

2. Создаем инвертированную бинарную маску `img_inv`: там, где на холсте есть рисунок, маска становится черной (`0`).

3. С помощью `bitwise_and` "вырезаем" область под рисунок на исходном кадре с веб-камеры.

4. С помощью `bitwise_or` накладываем цветные пиксели `canvas` на подготовленный кадр.


---


## 🛠️ Как менять и настраивать код


* **Изменить цвет кисти**:

В `main.py` измените кортеж `draw_color` в формате **BGR** (Blue, Green, Red):

```python

draw_color = (255, 0, 0) # Синий

draw_color = (0, 0, 255) # Красный

draw_color = (0, 255, 255) # Желтый

```


* **Изменить толщину кисти или ластика**:

```python

brush_thickness = 20 # Сделать кисть толще

eraser_thickness = 80 # Сделать ластик больше

```


* **Изменить разрешение веб-камеры**:

```python

cap.set(3, 1920) # Ширина

cap.set(4, 1080) # Высота

```


* **Настройка клавиш**:

Завершение работы происходит по нажатию клавиши **`q`**. Чтобы сменить клавишу, замените `'q'` на другую букву в строке:

```python

if cv2.waitKey(1) & 0xFF == ord('q'):

break

```


---


## 🚀 Что можно улучшить (Идеи для развития)


1. 🎨 **Интерактивная палитра цветов на экране**:

* Отрисовать в верхней части экрана цветные прямоугольники (красный, зеленый, синий, стиратель).

* При наведении указательного+среднего пальца в область прямоугольника автоматически переключать `draw_color`.


2. 📈 **Сглаживание линий (Moving Average / Bezier)**:

* Сейчас при быстром движении руки линии могут получаться угловатыми. Использование экспоненциального сглаживания или фильтра Калмана для координат `(x1, y1)` сделает рисование более плавным.


3. ↩️ **Отмена и повтор (Undo / Redo Stack)**:

* Хранить историю состояний `canvas` в списке (`deque`) для реализации отмены последнего штриха по жестку или горячей клавише (например, `Ctrl+Z`).


4. 💾 **Сохранение рисунка**:

* Добавить возможность сохранения текущего холста в файл (`.png` / `.jpg`) по нажатию клавиши (например, `s`) с помощью `cv2.imwrite('drawing.png', canvas)`.


5. 🎛️ **Изменение толщины кисти жестом**:

* Считывать расстояние между большим и указательным пальцем для динамического изменения толщины кисти прямо во время рисования.


6. 🏗️ **ООП-структура кода**:

* Вынести логику трекинга, обработки жестов и работы с холстом в отдельные классы (`HandTracker`, `CanvasManager`, `UIOverlay`). 
