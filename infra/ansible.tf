
provider "google" {
  project = "siva-477505"
  region  = "asia-south1"  # Mumbai
}

resource "google_compute_instance" "ansible_server" {
  name         = "ansible-server"
  machine_type = "e2-small"
  zone         = "asia-south1-a"
  
  tags = ["ansible"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  # MINIMAL: Just install Ansible
  metadata_startup_script = <<-EOF
#!/bin/bash
apt update
apt install -y ansible git
echo "Ansible $(ansible --version | head -1) ready"
EOF
}
