import sys

def _function_id(obj, nFramesUp):
	'''Create a string naming the function n frames up on the stack.'''
	fr = sys._getframe(nFramesUp+1)
	co = fr.f_code
	return "%s.%s" % (obj.__class__, co.co_name)


def not_implemented(obj=None):
	'''Use this instead of ``pass`` for the body of abstract methods.'''
	raise Exception("Unimplemented abstract method: %s" % _function_id(obj, 1))


class BaseResolver:
	def get_media_url(self, host, media_id):
		not_implemented(self)

	def get_url(self, host, media_id):
		not_implemented(self)

	def get_host_and_id(self, url):
		not_implemented(self)

	def valid_url(self, url, host):
		not_implemented(self)

	class __metaclass__(type):
		def __iter__(self):
			for attr in dir(BaseResolver):
				if not attr.startswith("__"):
					yield attr