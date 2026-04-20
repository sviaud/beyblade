"""Accès à la base de données de specs produit Nerf."""
import json


class ProductDatabase:
    def __init__(self, json_path):
        with open(json_path, encoding='utf-8') as f:
            self.data = json.load(f)

    def get(self, post_id):
        """Retourne les données d'un produit ou None."""
        return self.data.get(str(post_id))

    def has(self, post_id):
        return str(post_id) in self.data

    @staticmethod
    def default_faq(product_name, age_min=8, portee_m=None):
        """FAQ générique par défaut."""
        faqs = [
            {
                "q": f"Le {product_name} est-il adapté aux enfants ?",
                "a": f"Oui, le {product_name} est recommandé pour les enfants à partir de {age_min} ans. C'est l'âge minimum fixé par Hasbro pour une utilisation sûre et confortable.",
            },
        ]
        if portee_m:
            faqs.append({
                "q": f"Quelle est la portée réelle du {product_name} ?",
                "a": f"Le {product_name} atteint une portée d'environ {portee_m} mètres dans des conditions normales (tir horizontal, fléchettes en bon état).",
            })
        faqs.append({
            "q": f"Où acheter le {product_name} ?",
            "a": f"Le {product_name} est disponible sur Amazon.fr. Utilisez le bouton en bas de cet article pour accéder directement à la page produit.",
        })
        faqs.append({
            "q": f"Quelles munitions utiliser avec le {product_name} ?",
            "a": "Utilisez uniquement des fléchettes Nerf officielles correspondant au système du blaster pour garantir performances et sécurité.",
        })
        return faqs
