Vagrant::Config.run do |config|
  # Box
  config.vm.box = "lucid32_authentic2_001"
  config.vm.box_url = "http://192.168.0.2/lucid32_base_003.box"
  #config.vm.box_url = "http://192.168.0.2/lucid32_authentic2_001.box"


  # Shared Folders
  config.vm.share_folder("v-root", "/vagrant", ".", :nfs => true)
  #config.vm.share_folder("v-ssh", "/ssh", ENV["HOME"]+"/.ssh", :nfs => true)
  config.vm.share_folder("v-ssh", "/ssh", "/Volumes/Max/.ssh", :nfs => true)
  config.vm.network(:hostonly, "33.33.33.11")
end
