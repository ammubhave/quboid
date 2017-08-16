if (get_application_name() == "SecureWorkstationPanel") then
	set_window_workspace(2);
	set_window_strut(0, 0, 150, 0);
	set_skip_pager(true);
end

if (get_window_type() == "WINDOW_TYPE_NORMAL" and get_window_property("_QUBES_VMNAME") ~= "" and get_window_property("_QUBES_VMNAME") ~= "development" and get_window_property("_QUBES_VMNAME") ~= "sys-firewall") then
	maximize();
	undecorate_window();
	set_window_workspace(2);
	maximize();
end

