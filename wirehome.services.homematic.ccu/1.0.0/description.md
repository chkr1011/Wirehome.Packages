# Summary
Connects to the XML-RPC endpoint of a Homematic CCU and allows access to the device states.  
Offers an XML-RPC server to receive events from the CCU.

# Installation
- enable XML-RPC in the CCU Firewall configuration.

# Configuration
```
{
    "ccu_ip": "[IP of the CCU]",
    "ccu_port": "[PORT of the CCU's XML-RPC server]", // 2010 for Homematic IP devices, 2001 for BidCos-RF, 2000 for BidCos-Wired`
    "rpc_ip": "[IP of the Wirehome host]",
    "rpc_port": "[PORT of Wirehome's XML-RPC Server]" // choose one
}
```