using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using GoPro.Utils;
using Newtonsoft.Json.Linq;
using Windows.Globalization;
using Windows.Services.Store;
using Windows.Web.Http;

namespace GoPro.AppStore
{
	public class StoreService
	{
		public delegate void ErrorDelegate(StoreError error);

		internal class StoreData
		{
			public List<Product> StoreProducts;

			public List<Product> UserOwnedProducts;

			public List<Product> AvailableProducts;
		}

		[ComImport]
		[Guid("3E68D4BD-7135-4D10-8018-9FB6D9F33FA1")]
		[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
		private interface IInitializeWithWindow
		{
			void Initialize(IntPtr hwnd);
		}

		private static readonly List<Product> EMPTY_LIST_OF_PRODUCTS = new List<Product>();

		private static readonly List<string> STORE_PRODUCT_KINDS = new List<string> { "Durable", "Consumable", "UnmanagedConsumable", "Application" };

		private bool mIsOnline;

		private IStoreServiceContext mStoreContext;

		private Task<StoreData> mStoreDataTask;

		private IDispatcher mDispatcher;

		public bool IsOnline => mIsOnline;

		public ReadOnlyCollection<Product> UserOwnedProducts => ((mStoreContext != null) ? mStoreDataTask.Result.UserOwnedProducts : EMPTY_LIST_OF_PRODUCTS).AsReadOnly();

		public ReadOnlyCollection<Product> AvailableProducts => ((mStoreContext != null) ? mStoreDataTask.Result.AvailableProducts : EMPTY_LIST_OF_PRODUCTS).AsReadOnly();

		public ReadOnlyCollection<Product> StoreProducts => ((mStoreContext != null) ? mStoreDataTask.Result.StoreProducts : EMPTY_LIST_OF_PRODUCTS).AsReadOnly();

		public event ErrorDelegate OnError;

		public event Action<bool> SearchingForStoreProducts;

		public event Action Initialized;

		public StoreService(IDispatcher dispatcher)
		{
			mDispatcher = dispatcher;
			mStoreContext = null;
			mIsOnline = false;
		}

		public void Initialize(IStoreServiceContext storeContext)
		{
			mStoreContext = storeContext;
			Refresh();
		}

		public async Task Refresh()
		{
			mStoreDataTask = Task.Run(delegate
			{
				StoreData obj = new StoreData
				{
					StoreProducts = CreateStoreProductsInternal().Result
				};
				obj.UserOwnedProducts = obj.StoreProducts.Where((Product p) => p.IsOwnedByUser).ToList();
				return obj;
			}).ContinueWith(delegate(Task<StoreData> t)
			{
				StoreData result = t.Result;
				bool result2 = CheckSubscriptionPolicies().Result;
				result.AvailableProducts = (result2 ? result.StoreProducts.ToList() : new List<Product>());
				return result;
			}).ContinueWith(delegate(Task<StoreData> t)
			{
				mDispatcher.InvokeAsync(delegate
				{
					this.Initialized?.Invoke();
				});
				return t.Result;
			});
		}

		private async Task<List<Product>> CreateStoreProductsInternal()
		{
			mIsOnline = false;
			new List<Product>();
			this.SearchingForStoreProducts?.Invoke(obj: true);
			StoreProductQueryResultContainer storeProductQueryResultContainer = await mStoreContext.GetAssociatedStoreProductsAsync(STORE_PRODUCT_KINDS);
			this.SearchingForStoreProducts?.Invoke(obj: false);
			if (storeProductQueryResultContainer.ExtendedError != null)
			{
				List<Product> result = await GetUserProductsFromAppLicenseInternal();
				OnErrorInternal(StoreError.STORE_PRODUCT_QUERY_FAILED);
				return result;
			}
			List<Product> result2 = storeProductQueryResultContainer.Products.Values.ToList();
			mIsOnline = true;
			return result2;
		}

		private async Task<List<Product>> GetUserProductsFromAppLicenseInternal()
		{
			List<Product> products = new List<Product>();
			StoreAppLicenseContainer storeAppLicenseContainer = await mStoreContext.GetAppLicenseAsync();
			if (storeAppLicenseContainer == null)
			{
				return products;
			}
			foreach (StoreAddOnLicenseContainer value in storeAppLicenseContainer.AddOnLicenses.Values)
			{
				products.Add(new Product(AddOnLicense.ExtractStoreIdFromExtendedJsonData(value.ExtendedJsonData), isOwnedByUser: true));
			}
			return products;
		}

		private async Task<bool> CheckSubscriptionPolicies()
		{
			HttpClient val = new HttpClient();
			JObject jObject;
			try
			{
				string uriString = "https://software.gopro.com/desktop/staging/windows_subscription_policies.json";
				jObject = JObject.Parse(await val.GetStringAsync(new Uri(uriString)));
			}
			catch (Exception)
			{
				return false;
			}
			JObject obj = (JObject)jObject["gopro_sub"];
			JArray jArray = (JArray)obj["disallow_countries"];
			JArray jArray2 = (JArray)obj["disallow_currencies"];
			List<string> list = jArray?.ToObject<List<string>>();
			List<string> list2 = jArray2?.ToObject<List<string>>();
			GeographicRegion val2 = new GeographicRegion();
			if ((list != null && list.Contains(val2.get_CodeThreeLetter())) || (list2 != null && list2.Contains(val2.get_CurrenciesInUse()[0])))
			{
				return false;
			}
			return true;
		}

		public async Task<StorePurchaseStatus> Purchase(Product product, IntPtr activeWindowHandle)
		{
			if (product == null)
			{
				OnErrorInternal(StoreError.STORE_PRODUCT_PURCHASE_FAILED);
				return (StorePurchaseStatus)2;
			}
			if (mStoreContext.GetType() == typeof(MicrosoftStoreContext))
			{
				((IInitializeWithWindow)(mStoreContext as MicrosoftStoreContext).StoreContext).Initialize(activeWindowHandle);
			}
			StorePurchaseStatus status = (await mStoreContext.RequestPurchaseAsync(product.StoreId)).Status;
			if ((int)status == 3 || (int)status == 4)
			{
				OnErrorInternal(StoreError.STORE_PRODUCT_PURCHASE_FAILED);
				return status;
			}
			if ((int)status == 0 || (int)status == 1)
			{
				await Refresh();
			}
			return status;
		}

		public async Task<bool> CheckForUserAbsence()
		{
			StoreProductQueryResultContainer storeProductQueryResultContainer = await mStoreContext.GetUserCollectionAsync(STORE_PRODUCT_KINDS);
			return storeProductQueryResultContainer.ExtendedError != null && storeProductQueryResultContainer.ExtendedError.HResult == -2147023579;
		}

		private void OnErrorInternal(StoreError errorCode)
		{
			mDispatcher.InvokeAsync(delegate
			{
				this.OnError?.Invoke(errorCode);
			});
		}
	}
}
