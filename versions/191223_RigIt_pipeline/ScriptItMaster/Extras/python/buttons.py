hight = 60
width = 40
# icon and text
cmds.iconTextButton(l='label', style='iconAndTextVertical', image1="path/for/the/" + "fileName.png",
                    w=width, h=hight, c="command",
                    ann="Text to show when hovering over the button.")
# icon button
cmds.symbolButton(w=width, h=hight, image="path/for/the/" + "fileName.png", c="command"
                  ann="Text to show when hovering over the button.")
# regular button (text only)
cmds.button(l='label', w=width, h=hight, c="command",
            ann="Text to show when hovering over the button.")  # RN_T_icon