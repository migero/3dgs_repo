using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class StoreProductQueryResultContainer
	{
		public ReadOnlyDictionary<string, Product> Products { get; }

		public Exception ExtendedError { get; }

		public StoreProductQueryResultContainer(ReadOnlyDictionary<string, Product> products, Exception extendedError = null)
		{
			Products = products;
			ExtendedError = extendedError;
		}

		public StoreProductQueryResultContainer(StoreProductQueryResult result)
		{
			Dictionary<string, Product> dictionary = new Dictionary<string, Product>();
			foreach (StoreProduct value in result.get_Products().Values)
			{
				dictionary.Add(value.get_StoreId(), new Product(value.get_StoreId(), value.get_IsInUserCollection()));
			}
			Products = new ReadOnlyDictionary<string, Product>(dictionary);
			ExtendedError = result.get_ExtendedError();
		}
	}
}
