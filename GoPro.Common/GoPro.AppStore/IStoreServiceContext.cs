using System.Collections.Generic;
using System.Threading.Tasks;

namespace GoPro.AppStore
{
	public interface IStoreServiceContext
	{
		Task<StoreProductQueryResultContainer> GetAssociatedStoreProductsAsync(IEnumerable<string> productKinds);

		Task<StoreAppLicenseContainer> GetAppLicenseAsync();

		Task<StoreProductQueryResultContainer> GetUserCollectionAsync(IEnumerable<string> productKinds);

		Task<StorePurchaseResultContainer> RequestPurchaseAsync(string storeId);
	}
}
