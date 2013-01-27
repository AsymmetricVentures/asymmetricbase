import random
from asymmetricbase.tests.models import TestS3FileModel
from asymmetricbase.testing.base_with_models import BaseTestCaseWithModels

class TestS3File(BaseTestCaseWithModels):
	def test_simple_load_save(self):
		d1 = TestS3FileModel(file_data = "SOME FILE CONTENT")
		d2 = TestS3FileModel(file_data = "SOME OTHER FILE CONTENT")
		d3 = TestS3FileModel(file_data = "AND YET ANOTHER FILE CONTENT")
		d1.metadata = {'some_field': 'some value', 'another_field': 12345}
		d1.save()
		d2.save()
		d3.save()
		d1_loaded = TestS3FileModel.objects.get(id = d1.id)
		d2_loaded = TestS3FileModel.objects.get(id = d2.id)
		d3_loaded = TestS3FileModel.objects.get(id = d3.id)
		self.assertEquals(d1_loaded.file_data, "SOME FILE CONTENT")
		self.assertEquals(d2_loaded.file_data, "SOME OTHER FILE CONTENT")
		self.assertEquals(d3_loaded.file_data, "AND YET ANOTHER FILE CONTENT")
		self.assertEquals(d1_loaded.metadata, {'some_field': 'some value', 'another_field': 12345})
	
	def test_save_load_large_random_sized_blocks(self):
		random_blocks = []
		for i in range(10):
			random_blocks.append(self._generate_random_block())
		
		d_ids = []
		for i in range(10):
			d = TestS3FileModel(file_data = random_blocks[i])
			d.save()
			d_ids.append(d.id)
		self.assertEquals(len(d_ids), 10)
		
		for i in range(10):
			d_id = d_ids[i]
			d_loaded = TestS3FileModel.objects.get(id = d_id)
			self.assertEquals(d_loaded.file_data, random_blocks[i])
	
	def _generate_random_block(self):
		block_length = random.randrange(1000, 2000)
		return "".join(chr(random.randrange(0, 256)) for _i in xrange(block_length))
