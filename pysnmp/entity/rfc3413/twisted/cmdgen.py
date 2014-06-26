from twisted.internet import defer
from pysnmp.entity.rfc3413 import cmdgen
from pyasn1.compat.octets import null

def _cbFun(sendRequestHandle, errorIndication,
           errorStatus, errorIndex, varBinds, cbCtx):
    cbCtx.callback((errorIndication, errorStatus, errorIndex, varBinds))

class GetCommandGenerator(cmdgen.GetCommandGenerator):
    def sendReq(
        self,
        snmpEngine,
        addrName,
        varBinds,
        contextEngineId=None,
        contextName=null
        ):
        df = defer.Deferred()
        cmdgen.GetCommandGenerator.sendReq(
            self,
            snmpEngine,
            addrName,
            varBinds,
            _cbFun,
            df,
            contextEngineId,
            contextName
            )
        return df

class SetCommandGenerator(cmdgen.SetCommandGenerator):
    def sendReq(
        self,
        snmpEngine,
        addrName,
        varBinds,
        contextEngineId=None,
        contextName=null
        ):
        df = defer.Deferred()
        cmdgen.SetCommandGenerator.sendReq(
            self,
            snmpEngine,
            addrName,
            varBinds,
            _cbFun,
            df,
            contextEngineId,
            contextName
            )
        return df

def _cbFunWithDeferred(sendRequestHandle, errorIndication,
                       errorStatus, errorIndex, varBinds, cbCtx):
    df = cbCtx['df']
    df.callback(
        (errorIndication, errorStatus, errorIndex, varBinds)
        )
    # Callback function may return another deferred to indicate
    # it wishes to continue MIB walk.
    if isinstance(df.result, defer.Deferred):
        cbCtx['df'] = df.result
        return 1  # continue walking

class NextCommandGenerator(cmdgen.NextCommandGenerator):
    def sendReq(
        self,
        snmpEngine,
        addrName,
        varBinds,
        contextEngineId=None,
        contextName=null
        ):
        df = defer.Deferred()
        cmdgen.NextCommandGenerator.sendReq(
            self,
            snmpEngine,
            addrName,
            varBinds,
            _cbFunWithDeferred,
            { 'df': df },  # anonymous dictionary used for cbCtx
            contextEngineId,
            contextName
            )
        return df

class BulkCommandGenerator(cmdgen.BulkCommandGenerator):
    def sendReq(
        self,
        snmpEngine,
        addrName,
        nonRepeaters,
        maxRepetitions,
        varBinds,
        contextEngineId=None,
        contextName=null
        ):
        df = defer.Deferred()
        cmdgen.BulkCommandGenerator.sendReq(
            self,
            snmpEngine,
            addrName,
            nonRepeaters,
            maxRepetitions,
            varBinds,
            _cbFunWithDeferred,            
            { 'df': df },  # anonymous dictionary used for cbCtx
            contextEngineId=None,
            contextName=null
            )
        return df

