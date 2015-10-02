import sublime
import sublime_plugin
import subprocess
import os
import platform


class GodefCommand(sublime_plugin.WindowCommand):

    def run(self):
        print("=================[Godef]Begin=================")
        default_setting = sublime.load_settings("Preferences.sublime-settings")
        default_line_ending = default_setting.get("default_line_ending")
        print("[Godef]DEBUG: default_line_ending: %s" % default_line_ending)
        default_setting.set("default_line_ending", "unix")
        new_line_ending = default_setting.get("default_line_ending")
        print("[Godef]INFO: new_line_ending: %s" % new_line_ending)

        settings = sublime.load_settings("Godef.sublime-settings")
        gopath = settings.get("gopath", os.getenv('GOPATH'))
        if gopath is None:
            print("[Godef]ERROR: no GOPATH defined")
            print("=================[Godef] End =================")
            return

        systype = platform.system()
        print("[Godef]DEBUG: system type: %s" % systype)
        gopaths = gopath.split(os.pathsep)
        found = False
        godefpath = ""
        for path in gopaths:
            if(systype == "Windows"):
                godefCmd = "godef.exe"
            else:
                godefCmd = "godef"

            godefpath = os.path.join(path, "bin", godefCmd)

            if not os.path.isfile(godefpath):
                print("[Godef]WARN: godef not found at %s" % godefpath)
                continue
            else:
                print("[Godef]INFO: godef found at %s" % godefpath)
                found = True
                break

        if not found:
            print("[Godef]ERROR: godef not found!")
            print("=================[Godef] End =================")
            return
        else:
            print("[Godef]INFO: using godef: %s" % godefpath)

        view = self.window.active_view()
        # row, col = view.rowcol(view.sel()[0].begin())
        # offset = view.text_point(row, col)
        view = self.window.active_view()
        select = view.sel()[0]
        select_begin = select.begin()
        select_before = sublime.Region(0, select_begin)
        string_before = view.substr(select_before)
        string_before.encode("utf-8")
        buffer_before = bytearray(string_before, encoding="utf8")
        offset = len(buffer_before)
        print("[Godef]INFO: selcet_begin: %s offset: %s" %
              str(select_begin),
              str(offset))

        filename = view.file_name()
        args = [
            godefpath,
            "-f",
            filename,
            "-o",
            str(offset)
        ]
        print("[Godef]INFO: spawning: %s" % " ".join(args))

        env = os.environ.copy()
        env["GOPATH"] = gopath
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        output, stderr = p.communicate()
        if stderr:
            print("[Godef]ERROR: no definition found: %s" % str(stderr))
            print("=================[Godef] End =================")
            return

        location = output.decode("utf-8").rstrip().rsplit(":", 2)
        if len(location) == 3:
            print("[Godef]INFO: godef output: %s" % str(output))
            file = location[0]
            row = int(location[1])
            col = int(location[2])

            position = file + ":" + str(row) + ":" + str(col)
            print("[Godef]INFO: opening definition at %s" % position)
            view = self.window.open_file(position, sublime.ENCODED_POSITION)
        else:
            print("[Godef]ERROR: godef output bad: %s" % str(output))
        print("=================[Godef] End =================")
