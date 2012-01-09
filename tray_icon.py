from gi.repository import Gtk, Gdk, RB, Peas, GObject

class TrayIcon(GObject.Object, Peas.Activatable):

	__gtype_name = 'TrayIcon'
	object = GObject.property(type=GObject.Object)

	def popup_menu(self, icon, button, time, data = None):
		self.popup.popup(None, None, None, None, button, time)

	def toggle(self, icon, event, data = None):
		if event.button == 1: # left button
			self.wind.set_visible(not self.wind.get_visible())

	def play(self, widget):
		self.player.playpause(True) # does nothing argument

	def nextItem(self, widget):
		self.player.do_next()

	def previous(self, widget):
		self.player.do_previous()

	def hide_on_delete(self, widget, event):
		self.wind.hide()
		return True # don't actually delete

	def do_activate(self):
		self.shell = self.object
		self.wind = self.shell.get_property("window")
		self.player = self.shell.props.shell_player

		self.wind.connect("delete-event", self.hide_on_delete)

		ui = Gtk.UIManager()
		ui.add_ui_from_string(
		"""
		<ui>
		  <popup name='PopupMenu'>
			<menuitem action='PlayPause' />
			<menuitem action='Next' />
			<menuitem action='Previous' />
			<separator />
			<menuitem action='Quit' />
		  </popup>
		</ui>
		""")

		ag = Gtk.ActionGroup("actions")
		ag.add_actions([
				("PlayPause",Gtk.STOCK_MEDIA_PLAY,"Play/Pause",None, None, self.play),
				("Next",Gtk.STOCK_MEDIA_NEXT,"Next",None, None, self.nextItem),
				("Previous",Gtk.STOCK_MEDIA_PREVIOUS,"Previous",None, None, self.previous),
				("Quit",None,"Quit",None, None, Gtk.main_quit)
				])
		ui.insert_action_group(ag)
		self.popup = ui.get_widget("/PopupMenu")
		self.icon = Gtk.StatusIcon.new_from_file("/usr/share/pixmaps/rhythmbox-small.xpm")
		self.icon.connect("popup-menu", self.popup_menu)
		self.icon.connect("button-press-event", self.toggle)

	def do_deactivate(self):
		self.icon.set_visible(False)
		del self.icon
