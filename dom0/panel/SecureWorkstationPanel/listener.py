import signal
import subprocess
import xpybutil.ewmh as ewmh


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Wnck', '3.0')
    from gi.repository import Gtk, Wnck
    screen = Wnck.Screen.get_default()

    # ewmh.request_number_of_desktops_checked(1).check()

    def window_opened(a, w):
        wid = w.get_xid()
        vmname = subprocess.Popen(["/usr/bin/xprop", "-notype", "-id",
                                   str(wid), "_QUBES_VMNAME"],
                                  stdout=subprocess.PIPE).stdout.read().strip()

        vmname = vmname[16:]
        window_type = ewmh.get_wm_window_type(w.get_xid()).reply()
        # if window_type is None:
        #     window_type = 0
        # else:
        #     window_type = window_type[0]
        print(window_type, vmname)
        if vmname == "not found." and window_type[0] != 379:
            if window_type[0] == 372:
                return
            w.move_to_workspace(screen.get_workspace(0))
            return
        vmname = vmname[1:-1]

        names = ewmh.get_desktop_names().reply()[:-1]
        name_to_i = {name.split('|', 1)[0]: i for i, name in enumerate(names)}

        if vmname not in name_to_i:
            print("Workspace matching %s not found" % vmname)
            name_to_i[vmname] = 0
            # n = ewmh.get_number_of_desktops().reply() + 1
            # print(n)
            # ewmh.request_number_of_desktops_checked(n).check()
            # print(vmname)
            # names.append(vmname)
            # ewmh.set_desktop_names_checked(map(lambda x: x.encode('utf-8'),
            #                                    names + [""])).check()
            # name_to_i[vmname] = n - 1
        else:
            w.maximize()
            #print(dir(w))
            #w.undecorate_window()

        desktop_no = 0
        while desktop_no != name_to_i[vmname]:
            ewmh.request_wm_desktop_checked(wid, name_to_i[vmname])
            desktop_no = ewmh.get_wm_desktop(wid).reply()

    def window_closed(a, w):
        # w.get_workspace()
        # names = ewmh.get_desktop_names().reply()[:-1]
        pass

    screen.connect('window-opened', window_opened)
    screen.connect('window-closed', window_closed)
    Gtk.main()


if __name__ == "__main__":
    main()
