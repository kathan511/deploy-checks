# Homebrew Formula for deploy-check
# 
# To use this formula:
# 1. Create a tap repo: github.com/yourorg/homebrew-tools
# 2. Add this file as Formula/deploy-check.rb
# 3. Users install with: brew tap yourorg/tools && brew install deploy-check

class DeployCheck < Formula
  include Language::Python::Virtualenv

  desc "Pre-deployment validation tool with Terminal UI"
  homepage "https://github.com/yourorg/deploy-checks"
  url "https://github.com/yourorg/deploy-checks/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.11"

  resource "textual" do
    url "https://files.pythonhosted.org/packages/XX/textual-0.47.0.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/XX/rich-13.7.0.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/XX/markdown-it-py-3.0.0.tar.gz"
    sha256 "REPLACE_WITH_ACTUAL_SHA256"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Create a minimal test directory
    (testpath/"VERSION").write("1.0.0")
    
    # Check that the command runs
    assert_match "deploy-check", shell_output("#{bin}/deploy-check --help 2>&1", 0)
  end
end
