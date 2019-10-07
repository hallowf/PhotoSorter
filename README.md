
### Requirements

* Python 3
* Pillow
* wxPython for GUI interface need to be installed trough a wheel <- version used was 4.0.6
  * [Ubuntu](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04/)

#### Linux

**doing this also installs Pillow probably as a dependency of wxPython**

```
pip install -U \
  -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 \
  wxPython

```

#### Windows and MacOS

`pip install -U wxPython` or if you are in a virtual env `pip install wxPython` <-- not actually tested ....
