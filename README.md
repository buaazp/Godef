# Godef

This Sublime Text 2/3 [golang](http://golang.org/) plugin adds a `godef` command which uses [godef](http://godoc.org/github.com/rogpeppe/godef) or [guru](http://godoc.org/golang.org/x/tools/cmd/guru) to find the definition under the cursor.

#### Compatible with GoSublime

You can use this plugin working with [GoSublime](https://github.com/DisposaBoy/GoSublime) because GoSublime is not support `godef/guru`.

> This plugin support two different modes to find the definition of symbles:
> 
> `godef` offers faster speed. But cannot find correct definition if the package name is not matched with import path: [rogpeppe/godef#40](https://github.com/rogpeppe/godef/issues/40)
> 
> `guru` tool offers improved definition lookups which are compatible with Go 1.5+ vendoring.
> 
> We use `godef` to find definition first, if it fails, try `guru` again.

## Installation

The plugin assumes `godef/guru` is present at `$GOPATH/bin/`. You need install them first:

```
go get -v github.com/rogpeppe/godef
go get -v golang.org/x/tools/cmd/guru
```

#### Sublime Package Control

If you are using [Sublime Package Control](http://wbond.net/sublime_packages/package_control) you can simply install Sublime Godef by searching for `Godef` in the package listing.

#### Manual Install

Git clone this repository and place the entire `Godef` directory into your `Packages` directory.

OSX:

```
# Install the plugin
git clone git@github.com:buaazp/Godef.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Godef
```

Linux:

```
# Install the plugin
git clone git@github.com:buaazp/Godef.git ~/.config/sublime-text-3/Packages/Godef
```

Windows:

Now windows is been supported. Thanks for [@decker502](https://github.com/decker502) and [@mattn](https://github.com/mattn)'s work.  Please use the Sublime Package Control to install this plugin.

## Settings

### Configuring `GOPATH` and `GOROOT`

In most cases, you needn't set anything after installing. But if your `Godef` don't work you need to add gopath and goroot into the setting file before using this plugin. Here's an example `Godef.sublime-settings`:

```
{
	"goroot": "/Users/zippo/Go",
	"gopath": "/Users/zippo/gopath"
}

// or if you use windows
{
	"goroot": "C:\\Go",
	"gopath": "C:\\gopath"
}
```

NOTE: The value of `gopath/goroot` should be absolute path. Multiple path like env `GOPATH` are supported but relative path are not:

```
GOOD:
"gopath": "/opt/golang:/Users/zippo/develop/GO"

BAD:
"gopath": "~/develop/GO"
"gopath": "$HOME/develop/GO"
```

 This plugin will determine `GOPATH/GOROOT` from either:

1. The `gopath/goroot` value from `Godef.sublime-settings`
2. The `GOPATH/GOROOT` environment variable

NOTE 2: In case your plugin can't resolve internals, add the installed library path to your gopath (notice the last part):

```
"gopath": "/opt/golang:/Users/zippo/develop/GO:/usr/lib/go"
```

### Key Bindings

The default key of Godef is `gd`, which is also the default key of godef plugin for vim. Don't be afraid. This key binding will NOT modify your codes. Just press it.

Or you can click left button while pressing `super/ctrl+alt`. You CAN of course change it by yourself. Here's an example key binding:

```
{ "keys": ["super+h"], "command": "godef" }
```

You can also add these two key-binding into your keymap file to jump between the postions. Using j/k is because I use vim mode. Change them by yourself:

```
{ "keys": ["super+j"], "command": "jump_forward"},
{ "keys": ["super+k"], "command": "jump_back"},
```
These two command only available in ST3.

Enjoy it!

## Godef doesn't work

There are so many reasons lead to `godef` fails. If that happens, do these:

1. upgrade your plugin to the latest version.
2. press `ctrl + ~` to open the sublime console, then press godef shortcut key again.
3. logs in the console will show you the reason why `godef` is not work.
4. follow the logs and adjust your settings.
5. check if your `GOPATH/GOROOT` is right in settings.
6. open an issue and paste the logs in it.

## License

Godef is under BSD license which is in the license file.


