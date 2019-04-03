from graphics import GraphWin, Circle, Text, Point

def main():
    win = GraphWin('Lidar', 600, 400)  # give title and dimensions

    head = Circle(Point(40, 100), 25)  # set center and radius
    head.setFill("yellow")
    head.draw(win)

    label = Text(Point(100, 120), 'A face')
    label.draw(win)

    message = Text(Point(win.getWidth()/2, 20), 'Click anywhere to quit.')
    message.draw(win)
    win.getMouse()
    win.close()


main()
