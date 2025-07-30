output "instance" {
  value = aws_instance.this
}

output "eni" {
  value = aws_instance.this.primary_network_interface_id
}

output "az" {
  value = data.aws_network_interface.this.availability_zone
}