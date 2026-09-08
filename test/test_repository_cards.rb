require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../bin/repository-cards'

class RepositoryCardsTest < Minitest::Test
  SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>Repository</text></svg>'.freeze

  def setup
    @root = Dir.mktmpdir('repository-cards')
    FileUtils.mkdir_p(File.join(@root, '_data'))
    write_inventory(['WiiliamC/ez_tools', 'WiiliamC/codev'])
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def write_inventory(repos)
    File.write(File.join(@root, '_data/repositories.yml'), { 'github_repos' => repos }.to_yaml)
  end

  def write_cards(asset_root = @root)
    RepositoryCards.inventory(@root).each do |card|
      %w[light dark].each do |theme|
        path = File.join(asset_root, 'assets/img/repositories', "#{card['slug']}-#{theme}.svg")
        FileUtils.mkdir_p(File.dirname(path))
        File.write(path, SVG)
      end
    end
  end

  def test_matrix_preserves_order_case_and_template_naming
    cards = RepositoryCards.inventory(@root)
    assert_equal ['ez_tools', 'codev'], cards.map { |card| card['repo'] }
    assert_equal 'WiiliamC', cards.first['owner']
    assert_equal 'wiiliamc-ez-tools', cards.first['slug']
    output, = capture_io { RepositoryCards.main(['matrix', @root]) }
    assert_equal({ 'include' => cards }, JSON.parse(output))
  end

  def test_invalid_entries_and_filename_collisions
    [42, ['owner/repo/extra'], ['owner/..'], ['owner/repo&theme=dark'], [nil], ['owner/my_repo', 'OWNER/my-repo']].each do |repos|
      write_inventory(repos)
      assert_raises(ArgumentError) { RepositoryCards.inventory(@root) }
    end
  end

  def test_empty_list_needs_no_assets
    write_inventory([])
    assert_empty RepositoryCards.inventory(@root)
    assert_equal 0, RepositoryCards.check(@root, @root)
  end

  def test_new_repository_requires_both_themes
    write_cards
    assert_equal 4, RepositoryCards.check(@root, @root)
    write_inventory(['WiiliamC/ez_tools', 'WiiliamC/codev', 'owner/new_repo'])
    error = assert_raises(ArgumentError) { RepositoryCards.check(@root, @root) }
    assert_includes error.message, 'owner/new_repo (light)'
    assert_includes error.message, 'owner/new_repo (dark)'
  end

  def test_each_missing_theme_and_invalid_file_is_rejected
    %w[light dark].each do |theme|
      [nil, '', '<html>Not found</html>', '<svg>truncated'].each do |content|
        write_cards
        path = File.join(@root, "assets/img/repositories/wiiliamc-codev-#{theme}.svg")
        content.nil? ? File.unlink(path) : File.write(path, content)
        error = assert_raises(ArgumentError) { RepositoryCards.check(@root, @root) }
        assert_includes error.message, "WiiliamC/codev (#{theme})"
        assert_includes error.message, path
      end
    end
  end

  def test_production_artifact_must_contain_all_source_cards
    write_cards
    site = File.join(@root, '_site')
    assert_raises(ArgumentError) { RepositoryCards.check(@root, site) }
    write_cards(site)
    assert_equal 4, RepositoryCards.check(@root, site)
    File.unlink(File.join(site, 'assets/img/repositories/wiiliamc-codev-dark.svg'))
    assert_raises(ArgumentError) { RepositoryCards.check(@root, site) }
  end
end
