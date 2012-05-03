from asymmetricbase.logging import logger #@UnusedImport

class ForceRollback(Exception):
	""" Thrown to force a rollback within a commit_on_succes block """

class DeveloperTODO(Exception):
	""" Tell the user that the action is a work in progress""" 
