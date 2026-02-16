namespace GoPro.AppStore
{
	public class Product
	{
		private string mStoreId;

		private bool mIsOwnedByUser;

		public string StoreId => mStoreId;

		public bool IsOwnedByUser => mIsOwnedByUser;

		public Product(string storeId, bool isOwnedByUser)
		{
			mStoreId = storeId;
			mIsOwnedByUser = isOwnedByUser;
		}
	}
}
