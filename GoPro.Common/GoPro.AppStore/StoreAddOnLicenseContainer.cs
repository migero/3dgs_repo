using Newtonsoft.Json.Linq;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class StoreAddOnLicenseContainer
	{
		public string ExtendedJsonData { get; }

		public StoreAddOnLicenseContainer(string productId)
		{
			ExtendedJsonData = new JObject { 
			{
				AddOnLicense.PRODUCT_ID_PROPERTY_NAME,
				productId
			} }.ToString();
		}

		public StoreAddOnLicenseContainer(StoreLicense license)
		{
			ExtendedJsonData = license.get_ExtendedJsonData();
		}
	}
}
