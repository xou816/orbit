pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'orbit')
gnome = import('gnome')

gnome.compile_resources('orbit',
  'orbit.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'orbit.in',
  output: 'orbit',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

orbit_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'game/circle.py',
  'game/scene.py',
  'game/game.py',
  'game/player.py',
  'game/__init__.py',
]

install_data(orbit_sources, install_dir: moduledir)
