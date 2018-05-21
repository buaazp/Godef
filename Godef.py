import sublime
import sublime_plugin
import subprocess
import os
import platform
import sys
import json
from collections import deque


def real_path(go_path):
    if go_path is None:
        return None
    return os.path.expanduser(os.path.expandvars(go_path))


class GodefCommand(sublime_plugin.WindowCommand):
    """
    Godef command class
    use godef to find definition first,
    if not found, use guru to find again.
    """

    def __init__(self, window):
        self.systype = platform.system()
        self.gopath = None
        self.goroot = None
        self.cmdpaths = []
        self.env = None
        self.gosublime = {}
        self.read_gosublime(window)

        default_setting = sublime.load_settings("Preferences.sublime-settings")
        default_setting.set("default_line_ending", "unix")
        gopath = self._gopath()
        goroot = self._goroot()
        self.load(gopath, goroot, self.systype)
        self.gopath = gopath
        self.goroot = goroot
        if sys.version_info[0] == 2:
            super(GodefCommand, self).__init__(window)
        else:
            super().__init__(window)

    def load(self, gopath, goroot, systype):
        print("===============[Godef]Load Begin==============")
        # print("[Godef]DEBUG: system type: %s" % self.systype)
        if not gopath:
            print("[Godef]ERROR: no GOPATH defined")
            print("===============[Godef] Load End===============")
            return False

        if not goroot:
            print("[Godef]WARN: no GOROOT defined")

        cmdpaths = []
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
Make sure your gopath in settings is right.\n\
Use "go get -u github.com/rogpeppe/godef"\n\
and "go get -u golang.org/x/tools/cmd/guru"\n\
to install them.')
            print("===============[Godef] Load End===============")
            return False

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
        self.env = env
        print("===============[Godef] Load End===============")
        return True

    def run(self):
        default_setting = sublime.load_settings("Preferences.sublime-settings")
        default_setting.set("default_line_ending", "unix")
        settings = sublime.load_settings("Godef.sublime-settings")
        gopath = real_path(settings.get("gopath", os.getenv('GOPATH')))
        goroot = real_path(settings.get("goroot", os.getenv('GOROOT')))

        if self.gopath != gopath or self.goroot != goroot:
            print('[Godef]INFO: settings change, reload conf')
            self.gopath = gopath
            self.goroot = goroot
            self.cmdpaths = []
            self.env = None
        if len(self.cmdpaths) != 2 and not self.load(gopath, goroot, self.systype):
            return

        print("=================[Godef]Begin=================")
        if len(self.cmdpaths) == 1:
            if self.cmdpaths[0]['mode'] != 'godef':
                print('[Godef]WARN: missing cmd "godef"')
            else:
                print('[Godef]WARN: missing cmd "guru"')
        if not self.goroot:
            print("[Godef]WARN: no GOROOT defined in settings")

        view = self.window.active_view()
        filename = view.file_name()
        select = view.sel()[0]
        select_begin = select.begin()
        select_before = sublime.Region(0, select_begin)
        string_before = view.substr(select_before)
        offset = len(string_before.encode('utf-8'))
        if view.line_endings() == 'Windows':
            offset += string_before.count('\n')

        print("[Godef]INFO: select_begin: %s offset: %s" % (select_begin, offset))

        reset = False
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
                print("[Godef]EXPT: %s fail: %s" % (d['mode'], e))
                print('[Godef]WARN: %s binary not existed, need reload conf' % d['mode'])
                reset = True
                continue
            if stderr:
                err = stderr.decode("utf-8").rstrip()
                print("[Godef]ERROR: %s fail: %s" % (d['mode'], err))
                output = None
                continue
            elif len(output) < 3:
                position = output.decode("utf-8").rstrip()
                print("[Godef]ERROR: %s illegal output: %s" % (d['mode'], output))
                continue
            else:
                succ = d
                break

        if reset: self.cmdpaths = []

        if not output:
            print("[Godef]ERROR: all cmds failed")
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
        self.window.open_file(position, sublime.ENCODED_POSITION)
        # record prev postion
        startrow, startcol = view.rowcol(select_begin)
        GodefPrevCommand.append(filename, startrow, startcol)
        print("=================[Godef] End =================")

    def read_gosublime(self, window):
        """
        reads environment variables from gosublime.
        """
        view = window.active_view()
        if view is not None:
            settings = view.settings()
            gosublime = settings.get("GoSublime", None)
            if gosublime and gosublime.get("env", None):
                env = gosublime.get("env")
                print("[Godef]INFO: found gosublime environment: {env}".format(env=env))
                self.gosublime["gopath"] = env.get("GOPATH", "")
                self.gosublime["goroot"] = env.get("GOROOT", "")

    def _gopath(self):
        settings = sublime.load_settings("Godef.sublime-settings")
        gopath = real_path(settings.get("gopath", os.getenv('GOPATH')))
        if gopath is None:
            return self.gosublime.get("gopath", "")
        return gopath

    def _goroot(self):
        settings = sublime.load_settings("Godef.sublime-settings")
        goroot = real_path(settings.get("goroot", os.getenv('GOROOT')))
        if goroot is None:
            return self.gosublime.get("goroot", "")
        return goroot


# GodefPrev Commands
# code based on https://github.com/SublimeText/CTags/blob/development/ctagsplugin.py
class GodefPrevCommand(sublime_plugin.WindowCommand):
    """
    Provide ``godef_back`` command.

    Command "godef jump back" to the previous code point before a godef was navigated.

    This is functionality supported natively by ST3 but not by ST2. It is
    therefore included for legacy purposes.
    """
    buf = deque(maxlen=100)  # virtually a "ring buffer"

    def run(self):
        if not self.buf:
            print("[GodefPrev]ERROR: GodefPrev buffer empty")
            return

        filename, startrow, startcol = self.buf.pop()
        path = "{0}:{1}:{2}".format(filename, startrow +1, startcol + 1)
        self.window.open_file(path, sublime.ENCODED_POSITION)
        print("[GodefPrev]INFO: jump prev definition at %s" % path)

    @classmethod
    def append(cls, filename, startrow, startcol):
        """Append a code point to the list"""
        if filename:
            cls.buf.append((filename, startrow, startcol))
