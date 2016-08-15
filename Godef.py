import sublime
import sublime_plugin
import subprocess
import os
import platform
import sys
import json


class GodefCommand(sublime_plugin.WindowCommand):
    """
    Godef command class
    use godef to find definition first,
    if not found, use guru to find again.
    """

    def __init__(self, window):
        self.cmdpaths = None
        self.goroot = None
        self.env = None
        self.load()
        super().__init__(window)

    def load(self):
        print("===============[Godef]Init Begin==============")
        default_setting = sublime.load_settings("Preferences.sublime-settings")
        # default_line_ending = default_setting.get("default_line_ending")
        # print("[Godef]DEBUG: default_line_ending: %s" % default_line_ending)
        default_setting.set("default_line_ending", "unix")
        # new_line_ending = default_setting.get("default_line_ending")
        # print("[Godef]DEBUG: line_ending: %s" % new_line_ending)

        settings = sublime.load_settings("Godef.sublime-settings")
        gopath = settings.get("gopath", os.getenv('GOPATH'))

        if not gopath:
            print("[Godef]ERROR: no GOPATH defined")
            print("===============[Godef] Init End===============")
            return False

        cmdpaths = []
        systype = platform.system()
        # print("[Godef]DEBUG: system type: %s" % systype)
        for cmd in ['godef', 'guru']:
            found = False
            if systype == "Windows":
                binary = cmd + ".exe"
            else:
                binary = cmd
            gopaths = gopath.split(os.pathsep)
            for go_path in gopaths:
                cmdpath = os.path.join(go_path, "bin", binary)
                if not os.path.isfile(cmdpath):
                    print('[Godef]WARN: "%s" cmd not found at %s' % (cmd, go_path))
                    continue
                else:
                    found = True
                    break
            if not found:
                print('[Godef]WARN: "%s" cmd is not available.' % cmd)
                continue
            print('[Godef]INFO: found "%s" at %s' % (cmd, cmdpath))
            cmdpaths.append({'mode': cmd, 'path': cmdpath})

        if len(cmdpaths) == 0:
            print('[Godef]ERROR: godef/guru are not available.\n\
                   Use "go get -u github.com/rogpeppe/godef"\n\
                   and "go get -u golang.org/x/tools/cmd/guru"\n\
                   to install them.')
            print("===============[Godef] Init End===============")
            return False

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

        self.cmdpaths = cmdpaths
        self.goroot = goroot
        self.env = env
        print("===============[Godef] Init End===============")
        return True

    def run(self):
        if not self.cmdpaths and not self.load():
            return

        print("=================[Godef]Begin=================")
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

        output = None
        succ = None
        for d in self.cmdpaths:
            if 'godef' == d['mode']:
                args = [d['path'], "-f", filename, "-o", str(offset)]
            else:
                args = [d['path'], "-json", 'definition', filename + ":#" + str(offset)]
            print("[Godef]INFO: spawning: %s" % " ".join(args))

            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            stderr = None
            try:
                p = subprocess.Popen(args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, env=self.env,
                                     startupinfo=startupinfo)
                output, stderr = p.communicate()
            except Exception as e:
                print("[Godef]EXPT: %s fail: %s setting need reload" % (d['mode'], e))
                self.cmdpaths = None
                print("=================[Godef] End =================")
                return
            if stderr:
                err = stderr.decode("utf-8").rstrip()
                print("[Godef]ERROR: %s fail: %s" % (d['mode'], err))
                continue
                output = None
            else:
                succ = d
                break

        if not output:
            if len(self.cmdpaths) == 1 and 'godef' == self.cmdpaths[0]['mode']:
                print('[Godef]ERROR: maybe you can install cmd "guru" and try again')
            if not self.goroot:
                print("[Godef]ERROR: maybe no GOROOT defined in settings")
            print("=================[Godef] End =================")
            return

        position = output.decode("utf-8").rstrip()
        print("[Godef]INFO: %s output:\n%s" % (succ['mode'], position))
        if succ['mode'] == 'guru':
            definition = json.loads(position)
            if 'objpos' not in definition:
                print("[Godef]ERROR: guru result josn unmarshal err")
            else:
                position = definition['objpos']
        print("[Godef]INFO: opening definition at %s" % position)
        view = self.window.open_file(position, sublime.ENCODED_POSITION)
        print("=================[Godef] End =================")
