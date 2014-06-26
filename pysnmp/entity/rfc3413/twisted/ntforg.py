from twisted.internet import defer
from pysnmp.entity.rfc3413 import ntforg
from pyasn1.compat.octets import null

def _cbFun(sendRequestHandle, errorIndication,
           errorStatus, errorIndex, varBinds, cbCtx):
    cbCtx.callback((errorIndication, errorStatus, errorIndex, varBinds))

class NotificationOriginator(ntforg.NotificationOriginator):
    def sendNotification(
        self,
        snmpEngine,
        notificationTarget,
        notificationName,
        additionalVarBinds=None,
        contextName=null
        ):
        df = defer.Deferred()
        ntforg.NotificationOriginator.sendNotification(
            self,
            snmpEngine,
            notificationTarget,
            notificationName,
            additionalVarBinds,
            _cbFun,
            df,
            contextName=null
            )
        return df
