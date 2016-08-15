import sublime
import sublime_plugin
import subprocess
import os
import platform
import sys
import json


class GodefCommand(sublime_plugin.WindowCommand):
    def run(self):
        print("=================[Godef]Begin=================")
        default_setting = sublime.load_settings("Preferences.sublime-settings")
        # default_line_ending = default_setting.get("default_line_ending")
        # print("[Godef]DEBUG: default_line_ending: %s" % default_line_ending)
        default_setting.set("default_line_ending", "unix")
        # new_line_ending = default_setting.get("default_line_ending")
        # print("[Godef]DEBUG: line_ending: %s" % new_line_ending)

        settings = sublime.load_settings("Godef.sublime-settings")
        gopath = settings.get("gopath", os.getenv('GOPATH'))
        mode = settings.get("mode", 'guru')

        if mode not in ['guru', 'godef']:
            print("[Godef]ERROR: unsupported mode: %s" % mode)
            print("=================[Godef] End =================")
            return

        if not gopath:
            print("[Godef]ERROR: no GOPATH defined")
            print("=================[Godef] End =================")
            return

        systype = platform.system()
        # print("[Godef]DEBUG: system type: %s" % systype)
        if systype == "Windows":
            godefCmd = mode + ".exe"
        else:
            godefCmd = mode
        gopaths = gopath.split(os.pathsep)
        for go_path in gopaths:
            godefpath = os.path.join(go_path, "bin", godefCmd)
            if not os.path.isfile(godefpath):
                print('[Godef]WARN: "%s" cmd not found at %s' % (mode, godefpath))
                continue
            else:
                found = True
                break
        if not found:
            print('[Godef]ERROR: "%s" cmd is not available.\n\
                   Use "go get -u golang.org/x/tools/cmd/guru"\n\
                   or "go get -u github.com/rogpeppe/godef"\n\
                   to install.' % mode)
            print("=================[Godef] End =================")
            return
        print("[Godef]INFO: using cmd: %s" % godefpath)

        goroot = settings.get("goroot", os.getenv('GOROOT'))
        if not goroot:
            print("[Godef]WARN: no GOROOT defined")

        # a weird bug on windows. sometimes unicode strings end up in the
        # environment and subprocess.call does not like this, encode them
        # to latin1 and continue.
        env = os.environ.copy()
        if systype == "Windows":
            if sys.version_info[0] == 2:
                if gopath and isinstance(gopath, unicode):
                    gopath = gopath.encode('iso-8859-1')
                if goroot and isinstance(goroot, unicode):
                    goroot = goroot.encode('iso-8859-1')
        env["GOPATH"] = gopath
        if goroot:
            env["GOROOT"] = goroot

        view = self.window.active_view()
        filename = view.file_name()
        select = view.sel()[0]
        select_begin = select.begin()
        select_before = sublime.Region(0, select_begin)
        string_before = view.substr(select_before)
        string_before.encode("utf-8")
        buffer_before = bytearray(string_before, encoding="utf8")
        offset = len(buffer_before)
        print("[Godef]INFO: selcet_begin: %s offset: %s" %
              (str(select_begin), str(offset)))
        if mode == 'guru':
            args = [godefpath, "-json", 'definition', filename + ":#" + str(offset)]
        else:
            args = [godefpath, "-f", filename, "-o", str(offset)]
        print("[Godef]INFO: spawning: %s" % " ".join(args))

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env,
                             startupinfo=startupinfo)
        output, stderr = p.communicate()
        if stderr:
            err = stderr.decode("utf-8").rstrip()
            print("[Godef]ERROR: %s" % err)
            if mode != 'guru':
                print('[Godef]ERROR: maybe you can use recommended mode "guru" in settings')
            if not goroot:
                print("[Godef]ERROR: maybe no GOROOT defined in settings")
            print("=================[Godef] End =================")
            return

        position = output.decode("utf-8").rstrip()
        print("[Godef]INFO: %s output:\n%s" % (mode, position))
        if mode == 'guru':
            definition = json.loads(position)
            if 'objpos' not in definition:
                print("[Godef]ERROR: guru result josn unmarshal err")
            else:
                position = definition['objpos']
        print("[Godef]INFO: opening definition at %s" % position)
        view = self.window.open_file(position, sublime.ENCODED_POSITION)
        print("=================[Godef] End =================")
