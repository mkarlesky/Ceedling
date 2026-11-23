# Prints how Rake parses each task string given on the command line
require 'rake'
puts "Rake #{Rake::VERSION}"
ARGV.each { |s| puts "#{s} => #{Rake.application.parse_task_string(s).inspect}" }
