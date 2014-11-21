# This plugin is based on [GoTools](https://github.com/ironcladlou/GoTools) which is created by [Dan Mace](https://github.com/ironcladlou) and it's under MIT license:

# The MIT License (MIT)

# Copyright (c) 2014 Dan Mace

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sublime, sublime_plugin, subprocess, os, time

class GodefCommand(sublime_plugin.WindowCommand):
  def run(self):
    settings = sublime.load_settings("Godef.sublime-settings")
    gopath = settings.get("gopath", os.getenv('GOPATH'))
    if gopath is None:
      self.log("ERROR: no GOPATH defined")
      return

    self.gopath = gopath

    gopaths = gopath.split(":")
    found = False
    binpath = ""
    for path in gopaths:
      binpath = os.path.join(path, "bin", "godef")

      if not os.path.isfile(binpath):
        self.log("WARN: godef not found at", binpath)
        continue
      else:
        self.log("INFO: godef found at", binpath)
        found = True
        break

    if found == False:
      self.log("ERROR: godef not found!")
      return
    else:
      self.godefpath = binpath
      self.log("using godef:", self.godefpath)

    view = self.window.active_view()
    row, col = view.rowcol(view.sel()[0].begin())

    self.offset = view.text_point(row, col)
    self.filename = view.file_name()

    sublime.set_timeout_async(self.godef, 0)

  def godef(self):
    try:
      args = [
        self.godefpath,
        "-f",
        self.filename,
        "-o",
        str(self.offset)
      ]

      self.log("spawning", " ".join(args))

      env = os.environ.copy()
      env["GOPATH"] = self.gopath
      output = subprocess.check_output(args, stderr=subprocess.STDOUT, env=env)
    except subprocess.CalledProcessError as e:
      self.log("no definition found: ", e)
      return

    location = output.decode("utf-8").rstrip().split(":")

    file = location[0]
    row = int(location[1]) - 1
    col = int(location[2]) - 1

    self.log("opening definition at " + file + ":" + str(row) + ":" + str(col))
    view = self.window.open_file(file)

    while view.is_loading():
      time.sleep(0.01)

    region = sublime.Region(view.text_point(row, col))
    view.sel().clear()
    view.sel().add(region)
    view.show_at_center(region)

  def log(self, *messages):
    print("[Godef]", *messages)
