# Summary
Connects to the XML-RPC endpoint of Homematic CCU and allows access to the device states.

# Installation
- enable XML-RPC in the CCU Firewall configuration.

# Configuration
```
{
    "ip": "[IP of the CCU]",
    "port": "[PORT of the XML-RPC server]" // 2010 for Homematic IP devices, 2001 for BidCos-RF, 2000 for BidCos-Wired`
}
```