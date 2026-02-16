using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class MicrosoftStoreContext : IStoreServiceContext
	{
		public StoreContext StoreContext { get; private set; }

		public MicrosoftStoreContext(StoreContext storeContext)
		{
			StoreContext = storeContext;
		}

		public async Task<StoreAppLicenseContainer> GetAppLicenseAsync()
		{
			return new StoreAppLicenseContainer(await StoreContext.GetAppLicenseAsync());
		}

		public async Task<StoreProductQueryResultContainer> GetAssociatedStoreProductsAsync(IEnumerable<string> productKinds)
		{
			return new StoreProductQueryResultContainer(await StoreContext.GetAssociatedStoreProductsAsync(productKinds));
		}

		public async Task<StoreProductQueryResultContainer> GetUserCollectionAsync(IEnumerable<string> productKinds)
		{
			return new StoreProductQueryResultContainer(await StoreContext.GetUserCollectionAsync(productKinds));
		}

		public Task<StorePurchaseResultContainer> RequestPurchaseAsync(string storeId)
		{
			return Task.Run(() => new StorePurchaseResultContainer(StoreContext.RequestPurchaseAsync(storeId).AsTask<StorePurchaseResult>().Result));
		}
	}
}
