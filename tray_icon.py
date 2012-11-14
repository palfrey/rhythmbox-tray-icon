from gi.repository import Gtk, Gdk, GdkPixbuf, Peas, GObject, RB
import cairo

iconsPath = "/usr/share/icons/"
rhythmboxIcon = iconsPath + "hicolor/32x32/apps/rhythmbox.png"
playIcon = iconsPath + "gnome/32x32/actions/media-playback-start.png"

class TrayIcon(GObject.Object, Peas.Activatable):

	__gtype_name = 'TrayIcon'
	object = GObject.property(type=GObject.Object)

	def popup_menu(self, icon, button, time, data = None):
		self.popup.popup(None, None, None, None, button, time)

	def toggle(self, icon, event, data = None):
		if event.button == 1: # left button
			if self.wind.get_visible():
				self.wind.hide()
			else:
				self.wind.show()
				self.wind.present()
		elif event.button == 2: # middle button
			self.player.playpause(True)

	def play(self, widget):
		self.player.playpause(True) # does nothing argument

	def nextItem(self, widget):
		self.player.do_next()

	def previous(self, widget):
		self.player.do_previous()

 	def quit(self, widget):
		self.shell.quit()

	def hide_on_delete(self, widget, event):
		self.wind.hide()
		return True # don't actually delete

	def playing_changed(self, player, song):
		self.icon.set_tooltip_text(self.get_icon_title())
		if playing:
			self.icon.set_property("pixbuf", self.playIcon)
		else:
			self.icon.set_property("pixbuf", self.normalIcon)

	def playing_song_changed (self, player, song):
		self.icon.set_tooltip_text(self.get_icon_title())

	def playing_song_property_changed(self, player, uri, property, old, new):
		self.icon.set_tooltip_text(self.get_icon_title())

	def get_icon_title(self):
		self.shell = self.object
		self.player = self.shell.props.shell_player
		self.song = self.player.get_playing_entry()
		self.db = self.shell.get_property("db")
		try:
			self.current_title = self.song.get_string(RB.RhythmDBPropType.TITLE)
		except AttributeError:
			return "Not playing."
		#no stream: titel + artist
		#stream: stream_titel + titel
		if self.song.get_entry_type().props.category != RB.RhythmDBEntryCategory.STREAM:	#no stream
			self.current_artist = self.song.get_string(RB.RhythmDBPropType.ARTIST)
			return self.current_title + "\r" + self.current_artist
		else:		#stream
			self.current_stream_title = self.db.entry_request_extra_metadata(self.song, "rb:stream-song-title")
			if self.current_stream_title is None:
				return "\r" + self.current_title
			elif self.current_title is None:
				return self.current_stream_title + "\r"
			else:
				return self.current_stream_title + "\r" + self.current_title

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
				("Quit",None,"Quit",None, None, self.quit)
				])
		ui.insert_action_group(ag)
		self.popup = ui.get_widget("/PopupMenu")
		
		s1 = cairo.ImageSurface.create_from_png(rhythmboxIcon)
		s2 = cairo.ImageSurface.create_from_png(playIcon)
		ctx = cairo.Context(s1)
		ctx.set_source_surface(s2, 0, 0)
		ctx.paint()
		self.playIcon = Gdk.pixbuf_get_from_surface(s1, 0, 0, s1.get_width(), s1.get_height())

		self.normalIcon = GdkPixbuf.Pixbuf.new_from_file(rhythmboxIcon)
		self.icon = Gtk.StatusIcon.new_from_pixbuf(self.normalIcon)
		self.icon.set_tooltip_text(self.get_icon_title())
		self.icon.connect("scroll-event", self.scroll)
		self.icon.connect("popup-menu", self.popup_menu)
		self.icon.connect("button-press-event", self.toggle)
		self.player.connect("playing-changed", self.playing_changed)
		self.player.connect("playing-song-changed", self.playing_song_changed)
		self.player.connect("playing-song-property-changed", self.playing_song_property_changed)

	def scroll(self, widget, event):
		if self.player.playpause(True):
			# scroll up for previous track
			if event.direction == Gdk.ScrollDirection.UP:
				self.previous(widget)
			# scroll down for next track
			elif event.direction == Gdk.ScrollDirection.DOWN:
				self.nextItem(widget)

	def do_deactivate(self):
		self.icon.set_visible(False)
		del self.icon
