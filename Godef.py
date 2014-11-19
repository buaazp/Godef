import sublime, sublime_plugin, subprocess, os, time

class GodefCommand(sublime_plugin.WindowCommand):
  def run(self):
    settings = sublime.load_settings("Godef.sublime-settings")
    self.gopath = settings.get("gopath", os.getenv('GOPATH'))

    if self.gopath is None:
      self.log("ERROR: no GOPATH defined")
      return

    self.log("using gopath", self.gopath)

    view = self.window.active_view()
    row, col = view.rowcol(view.sel()[0].begin())

    self.offset = view.text_point(row, col)
    self.filename = view.file_name()

    sublime.set_timeout_async(self.godef, 0)

  def godef(self):
    godef_bin = os.path.join(self.gopath, "bin", "godef")

    if not os.path.isfile(godef_bin):
      self.log("ERROR: godef not found at", godef_bin)
      return

    try:
      args = [
        os.path.join(self.gopath, "bin", "godef"),
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
    col = int(location[2])

    self.log("opening definition at " + file + ":" + str(row) + ":" + str(col))
    view = self.window.open_file(file)

    while view.is_loading():
      time.sleep(0.01)

    region = sublime.Region(view.text_point(row, 0))
    view.sel().clear()
    view.sel().add(region)
    view.show_at_center(region)

  def log(self, *messages):
    print("[Godef]", *messages)
