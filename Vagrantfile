# -*- mode: ruby -*-
# vi: set ft=ruby :

    http_proxy_value = ENV['http_proxy'] 
    https_proxy_value = ENV['https_proxy']

Vagrant.configure("2") do |config|
 	config.vm.box = "centos/7"
  
 	config.vm.network "private_network", ip: "192.168.1.18",
        virtualbox__intnet: true
    
    # port forwarding - MAKE SURE HOST PORTS ARE NOT IN USE CURRENTLY
    config.vm.network :forwarded_port, guest:5000, host:5035    # Python Flask
    config.vm.network :forwarded_port, guest:5432, host:5034    
    config.vm.network :forwarded_port, guest:3306, host:5032    # mysql port

    # grab proxy stuff
  	if Vagrant.has_plugin?("vagrant-proxyconf")
    	config.proxy.http     = http_proxy_value
    	config.proxy.https    = https_proxy_value
    	config.proxy.no_proxy = "localhost,127.0.0.1"
  	end

    # provision with ansible playbook
    config.vm.provision "ansible_local" do |ansible|
        ansible.playbook = "provisioning/playbook.yml"
    end

    # set up synced folder
    config.vm.synced_folder ".", "/vagrant", type: "virtualbox"
end
