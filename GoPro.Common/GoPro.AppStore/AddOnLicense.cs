using System;
using Newtonsoft.Json.Linq;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class AddOnLicense
	{
		public static readonly string PRODUCT_ID_PROPERTY_NAME = "productId";

		private StoreLicense mStoreLicense;

		public DateTimeOffset ExpirationDate => mStoreLicense.get_ExpirationDate();

		public bool IsActive => mStoreLicense.get_IsActive();

		public string SkuStoreId => mStoreLicense.get_SkuStoreId();

		public AddOnLicense(StoreLicense license)
		{
			mStoreLicense = license;
		}

		public static string ExtractStoreIdFromExtendedJsonData(string extendedJsonData)
		{
			return JObject.Parse(extendedJsonData).GetValue(PRODUCT_ID_PROPERTY_NAME)!.ToString();
		}
	}
}
