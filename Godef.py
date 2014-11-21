import sublime, sublime_plugin, subprocess, os, time

class GodefCommand(sublime_plugin.WindowCommand):
  def run(self):
    settings = sublime.load_settings("Godef.sublime-settings")
    gopath = settings.get("gopath", os.getenv('GOPATH'))
    if gopath is None:
      print "ERROR: no GOPATH defined"
      return

    gopaths = gopath.split(":")
    found = False
    godefpath = ""
    for path in gopaths:
      godefpath = os.path.join(path, "bin", "godef")

      if not os.path.isfile(godefpath):
        # print "WARN: godef not found at" + godefpath
        continue
      else:
        # print "INFO: godef found at" + godefpath
        found = True
        break

    if found == False:
      print "ERROR: godef not found!"
      return
    # else:
    #   print "using godef:" + godefpath

    view = self.window.active_view()
    row, col = view.rowcol(view.sel()[0].begin())

    offset = view.text_point(row, col)
    filename = view.file_name()

    args = [
      godefpath,
      "-f",
      filename,
      "-o",
      str(offset)
    ]

    # print "spawning: " + " ".join(args)

    env = os.environ.copy()
    env["GOPATH"] = gopath
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    output, stderr = p.communicate()
    if stderr:
      print ("no definition found: " + stderr)
      return

    # print "godef output: " + output

    location = output.decode("utf-8").rstrip().split(":")

    file = location[0]
    row = int(location[1])
    col = int(location[2])

    postion = (file + ":" + str(row) + ":" + str(col))
    # print("opening definition at " + postion)
    view = self.window.open_file(postion, sublime.ENCODED_POSITION)
    # view.show_at_center(region)

