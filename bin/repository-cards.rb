#!/usr/bin/env ruby
# Site-owned repository card inventory, shared by CI and production checks.
require 'json'
require 'yaml'

module RepositoryCards
  def self.inventory(root)
    data = YAML.safe_load_file(File.join(root, '_data/repositories.yml'))
    raise ArgumentError, 'repositories.yml must contain a mapping' unless data.is_a?(Hash)

    repos = data.fetch('github_repos', []) || []
    raise ArgumentError, 'github_repos must be an array' unless repos.is_a?(Array)

    slugs = {}
    repos.map do |repository|
      unless repository.is_a?(String) && repository.match?(%r{\A[A-Za-z0-9-]+/[A-Za-z0-9_.-]+\z}) && !%w[. ..].include?(repository.split('/').last)
        raise ArgumentError, "Invalid repository: #{repository.inspect} (expected owner/repo)"
      end
      owner, repo = repository.split('/')
      slug = repository.downcase.tr('/_', '--')
      raise ArgumentError, "Card filename collision: #{slugs[slug]} and #{repository}" if slugs.key?(slug)

      slugs[slug] = repository
      { 'owner' => owner, 'repo' => repo, 'slug' => slug }
    end
  end

  def self.check(root, asset_root)
    errors = []
    cards = inventory(root)
    cards.each do |card|
      %w[light dark].each do |theme|
        path = File.join(asset_root, 'assets/img/repositories', "#{card.fetch('slug')}-#{theme}.svg")
        content = File.file?(path) ? File.read(path) : ''
        # Reject missing/empty files and HTTP error pages saved instead of SVGs.
        unless content.match?(/\A\s*(?:<\?xml[^>]*>\s*)?(?:<!--.*?-->\s*)*<svg(?=\s|>)/m) && content.match?(%r{</svg>\s*\z})
          errors << "#{card.fetch('owner')}/#{card.fetch('repo')} (#{theme}): missing, empty or invalid SVG: #{path}"
        end
      end
    end
    raise ArgumentError, errors.join("\n") unless errors.empty?

    cards.length * 2
  end

  def self.main(args)
    command, root, asset_root = args
    root ||= File.expand_path('..', __dir__)
    case command
    when 'matrix'
      cards = inventory(root)
      puts JSON.generate('include' => cards)
    when 'check'
      puts "Validated #{check(root, asset_root || root)} repository card SVGs."
    else
      raise ArgumentError, 'Usage: ruby bin/repository-cards.rb matrix [root] | check [root] [asset-root]'
    end
  end
end

if $PROGRAM_NAME == __FILE__
  begin
    RepositoryCards.main(ARGV)
  rescue ArgumentError, KeyError, Psych::Exception, SystemCallError => e
    warn e.message
    exit 1
  end
end
