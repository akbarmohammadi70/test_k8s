terraform {
  required_providers {
    arvan = {
      source = "terraform.arvancloud.ir/arvancloud/iaas"
    }
  }
}

variable "api_key" {
  type        = string
  description = "The API key for Arvan Cloud"
}

provider "arvan" {
  api_key = var.api_key
}

variable "region" {
  type        = string
  description = "The region to deploy resources in"
  default     = "ir-thr-ba1"
}

variable "network_id" {
  type        = string
  description = "The chosen id of network"
}

variable "chosen_plan_id" {
  type        = string
  description = "The chosen ID of plan"
}

variable "security_group_id" {
  type        = string
  description = "The security group ID to apply to the instances"
}

variable "image_id" {
  type        = string
  description = "The Image ID to apply to the instances"
}

resource "arvan_abrak" "kubernetes_nodes" {
  timeouts {
    create = "2h"
    update = "2h"
    delete = "20m"
    read   = "10m"
  }
  count        = 3
  region       = var.region
  name         = "node${count.index + 1}"
  image_id     = var.image_id
  flavor_id    = var.chosen_plan_id
  disk_size    = 50
  ssh_key_name = "mac"
  networks = [
    {
      network_id = var.network_id
    }
  ]
  security_groups = [var.security_group_id]
}

output "kubernetes_nodes" {
  value = arvan_abrak.kubernetes_nodes
}