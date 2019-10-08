### Running tests

`python -m unittest discover -s tests/`


### Requirements

* virtualenv <- reccomended
* Python 3 <- 3.6.8 was used in development
* Pillow
* wxPython for GUI interface need to be installed trough a wheel on linux <- version used was 4.0.6
  * [Ubuntu](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04/)
  * [Others](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/)

#### Linux

**doing this also installs Pillow probably as a dependency of wxPython**

```

pip install -U \
  -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 \
  wxPython

```

#### Windows and MacOS

`pip install -U wxPython` or if you are in a virtual env `pip install wxPython` <-- not actually tested ....
