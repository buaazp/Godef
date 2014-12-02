import sublime, sublime_plugin, subprocess, os, time

class GodefCommand(sublime_plugin.WindowCommand):
  def run(self):
    print("=================[Godef]Begin=================")
    settings = sublime.load_settings("Godef.sublime-settings")
    gopath = settings.get("gopath", os.getenv('GOPATH'))
    if gopath is None:
      print("[Godef]ERROR: no GOPATH defined")
      print("=================[Godef] End =================")
      return

    gopaths = gopath.split(":")
    found = False
    godefpath = ""
    for path in gopaths:
      godefpath = os.path.join(path, "bin", "godef")

      if not os.path.isfile(godefpath):
        print("[Godef]WARN: godef not found at" + godefpath)
        continue
      else:
        print("[Godef]INFO: godef found at" + godefpath)
        found = True
        break

    if found == False:
      print("[Godef]ERROR: godef not found!")
      print("=================[Godef] End =================")
      return
    else:
      print("[Godef]INFO: using godef:" + godefpath)

    view = self.window.active_view()

    # row, col = view.rowcol(view.sel()[0].begin())

    # offset = view.text_point(row, col)

    view = self.window.active_view()
    select = view.sel()[0]
    select_begin = select.begin()
    select_before = sublime.Region(0, select_begin)
    string_before = view.substr(select_before)
    string_before.encode("utf-8")
    buffer_before = bytearray(string_before, encoding = "utf8")
    offset = len(buffer_before)
    print("[Godef]INFO: selcet_begin: " + str(select_begin) + " offset: " + str(offset))

    filename = view.file_name()

    args = [
      godefpath,
      "-f",
      filename,
      "-o",
      str(offset)
    ]

    print("[Godef]INFO: spawning: " + " ".join(args))

    env = os.environ.copy()
    env["GOPATH"] = gopath
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    output, stderr = p.communicate()
    if stderr:
      print("[Godef]ERROR: no definition found: " + str(stderr))
      print("=================[Godef] End =================")
      return

    location = output.decode("utf-8").rstrip().split(":")

    if len(location) == 3:
      print("[Godef]INFO: godef output: " + str(output))
      file = location[0]
      row = int(location[1])
      col = int(location[2])

      postion = (file + ":" + str(row) + ":" + str(col))
      print("[Godef]INFO: opening definition at " + postion)
      view = self.window.open_file(postion, sublime.ENCODED_POSITION)
      # view.show_at_center(region)
    else:
      print("[Godef]ERROR: godef output bad: " + str(output))
    print("=================[Godef] End =================")

