def Btn_Style():
    return """
                       QPushButton {
                           background-color: #e0e0e0;  /* 按钮背景色（浅灰） */
                           color: black;               /* 文字颜色 */
                           border-radius: 10px;        /* 圆角 */
                           font-size: 18px;            /* 字体大小 */
                           padding: 10px;              /* 内边距 */
                           border: 2px solid #e0e0e0;  /* 按钮边框 */
                       }
                       QPushButton:hover {
                           background-color: #c0c0c0;  /* 鼠标悬停时变深 */
                       }
                   """